# Changelog

## Version 1.0

### Changed

- Some endpoints did not respect the token OAuth scope, resulting in tokens
  with only read permissions being allowed to perform write operations. If you
  want to do keep doing write operations request "read write" permissions, see
  example in [update_inventory.py](update_inventory.py)

### Added

- The service can throttle clients performing an excessive number of requests
  in a short period of time. Clients should implement back-off strategies if
  the client receives HTTP code 429 Too Many Requests.
