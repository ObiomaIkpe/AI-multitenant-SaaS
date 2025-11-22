from llama_index.core.vector_stores.types import MetadataFilters, MetadataFilter, ExactMatchFilter, FilterOperator

def build_metadata_filters(tenant_id: str, request):
    filters = [ExactMatchFilter(key="tenant_id", value=tenant_id)]
    
    if request.document_ids:
        filters.append(MetadataFilter(key="document_id", value=request.document_ids, operator=FilterOperator.IN))
    if request.categories:
        filters.append(MetadataFilter(key="category", value=request.categories, operator=FilterOperator.IN))
    if request.tags:
        filters.append(MetadataFilter(key="tags", value=request.tags, operator=FilterOperator.IN))
    if request.file_types:
        filters.append(MetadataFilter(key="file_type", value=request.file_types, operator=FilterOperator.IN))
    if request.date_from:
        filters.append(MetadataFilter(key="upload_date", value=request.date_from, operator=FilterOperator.GTE))
    if request.date_to:
        filters.append(MetadataFilter(key="upload_date", value=request.date_to, operator=FilterOperator.LTE))
    
    return MetadataFilters(filters=filters)

def get_applied_filters_summary(request):
    summary = {}
    if request.document_ids: summary["document_ids"] = request.document_ids
    if request.categories: summary["categories"] = request.categories
    if request.tags: summary["tags"] = request.tags
    if request.file_types: summary["file_types"] = request.file_types
    if request.date_from or request.date_to: summary["date_range"] = {"from": request.date_from, "to": request.date_to}
    if not summary: summary["scope"] = "all_documents"
    return summary