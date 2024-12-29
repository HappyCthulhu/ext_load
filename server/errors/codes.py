# For cases when other instances have relation on this one and their on_delete is set to PROTECTED.
protected_instance: int = 1
# For cases when exception was not gracefully handled.
unhandled_error: int = 2
# For permission denials
permission_denied: int = 3
# When internal database inconsistencies are detected
internal_data_inconsistency: int = 4
# When requested object does not exist
does_not_exist: int = 5
# When data supplied from client is invalid
invalid_request_data: int = 6
# When there is a conflict with the current state of the resource
conflict: int = 7

# TODO: сделать код для бага на серваке? в духе "код написан неграмотно"

# Custom HTTP status codes for internal error codes
status_code_mapping: dict[int, int] = {
    protected_instance: 500,
    unhandled_error: 500,
    permission_denied: 403,
    internal_data_inconsistency: 500,
    does_not_exist: 404,
    invalid_request_data: 400,
    conflict: 409,
}
