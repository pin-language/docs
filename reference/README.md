# Pin built-in reference

Every built-in function, constant and cast in Pin, grouped by topic. Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); the examples are compiled and run by its test suite.

New to Pin? Start with the [language guide](../language.md). Writing Pin with an AI agent? Give it the [AI guide](../ai-guide.md).

## [Strings](strings.md)

[`strlen`](strings.md#strlen), [`substr`](strings.md#substr), [`strpos`](strings.md#strpos), [`str_contains`](strings.md#str_contains), [`str_starts_with`](strings.md#str_starts_with), [`str_ends_with`](strings.md#str_ends_with), [`str_repeat`](strings.md#str_repeat), [`strtolower`](strings.md#strtolower), [`strtoupper`](strings.md#strtoupper), [`trim`](strings.md#trim), [`explode`](strings.md#explode), [`implode`](strings.md#implode), [`PHP_EOL`](strings.md#php_eol)

## [Lists and maps](lists-and-maps.md)

[`count`](lists-and-maps.md#count), [`fill`](lists-and-maps.md#fill), [`copy`](lists-and-maps.md#copy), [`sort`](lists-and-maps.md#sort), [`rsort`](lists-and-maps.md#rsort), [`isset`](lists-and-maps.md#isset), [`array_key_exists`](lists-and-maps.md#array_key_exists), [`unset`](lists-and-maps.md#unset)

## [Numbers](numbers.md)

[`intdiv`](numbers.md#intdiv), [`sqrt`](numbers.md#sqrt), [`wrapping_add`](numbers.md#wrapping_add), [`wrapping_sub`](numbers.md#wrapping_sub), [`wrapping_mul`](numbers.md#wrapping_mul), [`PHP_INT_MAX`](numbers.md#php_int_max), [`PHP_INT_MIN`](numbers.md#php_int_min)

## [Conversions](conversions.md)

[`intval`](conversions.md#intval), [`floatval`](conversions.md#floatval), [`strval`](conversions.md#strval), [`(int)`](conversions.md#int), [`(float)`](conversions.md#float), [`(string)`](conversions.md#string)

## [JSON](json.md)

[`json_encode`](json.md#json_encode), [`json_has`](json.md#json_has), [`json_string`](json.md#json_string), [`json_int`](json.md#json_int), [`json_float`](json.md#json_float), [`json_bool`](json.md#json_bool)

## [HTTP](http.md)

[`serve`](http.md#serve), [`http_status`](http.md#http_status), [`url_path`](http.md#url_path), [`query_param`](http.md#query_param), [`query_has`](http.md#query_has), [`form_param`](http.md#form_param), [`form_has`](http.md#form_has)

## [Database (SQLite)](database.md)

[`db_open`](database.md#db_open), [`db_exec`](database.md#db_exec), [`db_query`](database.md#db_query), [`db_next`](database.md#db_next), [`db_int`](database.md#db_int), [`db_float`](database.md#db_float), [`db_string`](database.md#db_string), [`db_is_null`](database.md#db_is_null), [`db_json`](database.md#db_json), [`db_last_id`](database.md#db_last_id), [`db_error`](database.md#db_error)

## [Errors](errors.md)

[`error`](errors.md#error)
