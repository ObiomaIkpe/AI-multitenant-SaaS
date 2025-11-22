import httpx
import hmac
import hashlib
import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Webhook
from datetime import datetime

async def trigger_webhook(
    db: AsyncSession,
    tenant_id: str,
    event: str,
    payload: Dict[str, Any]
):
    """Trigger webhooks for a specific event"""
    
    # Find active webhooks for this tenant and event
    result = await db.execute(
        select(Webhook).where(
            Webhook.tenant_id == tenant_id,
            Webhook.is_active == True
        )
    )
    webhooks = result.scalars().all()
    
    for webhook in webhooks:
        # Check if webhook is subscribed to this event
        if event not in webhook.events:
            continue
        
        # Prepare payload
        webhook_payload = {
            "event": event,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        
        # Generate signature
        signature = hmac.new(
            webhook.secret.encode(),
            json.dumps(webhook_payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Send webhook (async, don't block)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    json=webhook_payload,
                    headers={
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event,
                        "Content-Type": "application/json"
                    }
                )
                
                # Update stats
                webhook.total_deliveries += 1
                webhook.last_triggered_at = datetime.utcnow()
                
                if response.status_code >= 400:
                    webhook.failed_deliveries += 1
                    print(f"Webhook failed: {webhook.url} - Status {response.status_code}")
                
        except Exception as e:
            webhook.failed_deliveries += 1
            print(f"Webhook error: {webhook.url} - {str(e)}")
    
    await db.commit()