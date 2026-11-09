# Pin built-in reference

Every built-in function, constant and cast in Pin, grouped by topic. Generated from `spec/pin_builtins.py` in the [pin repository](https://github.com/pin-language/pin); the examples are compiled and run by its test suite.

New to Pin? Start with the [language guide](../language.md). Writing Pin with an AI agent? Give it the [AI guide](../ai-guide.md).

## [Strings](strings.md)

[`ord`](strings.md#ord), [`chr`](strings.md#chr), [`rawurlencode`](strings.md#rawurlencode), [`strlen`](strings.md#strlen), [`substr`](strings.md#substr), [`mb_strlen`](strings.md#mb_strlen), [`mb_substr`](strings.md#mb_substr), [`mb_strpos`](strings.md#mb_strpos), [`mb_chr`](strings.md#mb_chr), [`mb_ord`](strings.md#mb_ord), [`grapheme_strlen`](strings.md#grapheme_strlen), [`grapheme_substr`](strings.md#grapheme_substr), [`mb_strtolower`](strings.md#mb_strtolower), [`mb_strtoupper`](strings.md#mb_strtoupper), [`normalizer_normalize`](strings.md#normalizer_normalize), [`strpos`](strings.md#strpos), [`str_contains`](strings.md#str_contains), [`str_starts_with`](strings.md#str_starts_with), [`str_ends_with`](strings.md#str_ends_with), [`str_repeat`](strings.md#str_repeat), [`strtolower`](strings.md#strtolower), [`strtoupper`](strings.md#strtoupper), [`trim`](strings.md#trim), [`sprintf`](strings.md#sprintf), [`printf`](strings.md#printf), [`str_pad`](strings.md#str_pad), [`STR_PAD_LEFT`](strings.md#str_pad_left), [`STR_PAD_RIGHT`](strings.md#str_pad_right), [`STR_PAD_BOTH`](strings.md#str_pad_both), [`ucwords`](strings.md#ucwords), [`strrev`](strings.md#strrev), [`is_numeric`](strings.md#is_numeric), [`str_replace`](strings.md#str_replace), [`ltrim`](strings.md#ltrim), [`rtrim`](strings.md#rtrim), [`ucfirst`](strings.md#ucfirst), [`lcfirst`](strings.md#lcfirst), [`htmlspecialchars`](strings.md#htmlspecialchars), [`base64_encode`](strings.md#base64_encode), [`base64_decode`](strings.md#base64_decode), [`rawurldecode`](strings.md#rawurldecode), [`urldecode`](strings.md#urldecode), [`number_format`](strings.md#number_format), [`explode`](strings.md#explode), [`implode`](strings.md#implode), [`PHP_EOL`](strings.md#php_eol)

## [Lists and maps](lists-and-maps.md)

[`array_pop`](lists-and-maps.md#array_pop), [`array_shift`](lists-and-maps.md#array_shift), [`array_slice`](lists-and-maps.md#array_slice), [`array_merge`](lists-and-maps.md#array_merge), [`array_reverse`](lists-and-maps.md#array_reverse), [`array_search`](lists-and-maps.md#array_search), [`array_unique`](lists-and-maps.md#array_unique), [`in_array`](lists-and-maps.md#in_array), [`array_keys`](lists-and-maps.md#array_keys), [`array_values`](lists-and-maps.md#array_values), [`array_sum`](lists-and-maps.md#array_sum), [`count`](lists-and-maps.md#count), [`fill`](lists-and-maps.md#fill), [`copy`](lists-and-maps.md#copy), [`sort`](lists-and-maps.md#sort), [`rsort`](lists-and-maps.md#rsort), [`isset`](lists-and-maps.md#isset), [`array_key_exists`](lists-and-maps.md#array_key_exists), [`unset`](lists-and-maps.md#unset)

## [Numbers](numbers.md)

[`date`](numbers.md#date), [`intdiv`](numbers.md#intdiv), [`round`](numbers.md#round), [`floor`](numbers.md#floor), [`ceil`](numbers.md#ceil), [`abs`](numbers.md#abs), [`max`](numbers.md#max), [`min`](numbers.md#min), [`sqrt`](numbers.md#sqrt), [`wrapping_add`](numbers.md#wrapping_add), [`wrapping_sub`](numbers.md#wrapping_sub), [`wrapping_mul`](numbers.md#wrapping_mul), [`time`](numbers.md#time), [`PHP_INT_MAX`](numbers.md#php_int_max), [`PHP_INT_MIN`](numbers.md#php_int_min)

## [Conversions](conversions.md)

[`intval`](conversions.md#intval), [`floatval`](conversions.md#floatval), [`strval`](conversions.md#strval), [`(int)`](conversions.md#int), [`(float)`](conversions.md#float), [`(string)`](conversions.md#string)

## [JSON](json.md)

[`JSON_PRETTY_PRINT`](json.md#json_pretty_print), [`JSON_UNESCAPED_SLASHES`](json.md#json_unescaped_slashes), [`JSON_UNESCAPED_UNICODE`](json.md#json_unescaped_unicode), [`JSON_THROW_ON_ERROR`](json.md#json_throw_on_error), [`json_encode`](json.md#json_encode), [`json_raw`](json.md#json_raw), [`json_len`](json.md#json_len), [`json_at`](json.md#json_at), [`json_has`](json.md#json_has), [`json_decode`](json.md#json_decode), [`json_string`](json.md#json_string), [`json_int`](json.md#json_int), [`json_float`](json.md#json_float), [`json_bool`](json.md#json_bool)

## [HTTP](http.md)

[`serve`](http.md#serve), [`http_status`](http.md#http_status), [`request_header`](http.md#request_header), [`request_has_header`](http.md#request_has_header), [`request_ip`](http.md#request_ip), [`response_header`](http.md#response_header), [`url_path`](http.md#url_path), [`query_param`](http.md#query_param), [`query_has`](http.md#query_has), [`form_param`](http.md#form_param), [`form_has`](http.md#form_has), [`request_deadline`](http.md#request_deadline), [`sse_start`](http.md#sse_start), [`sse_send`](http.md#sse_send), [`sse_send_id`](http.md#sse_send_id), [`sse_comment`](http.md#sse_comment)

## [Database (SQLite)](database.md)

[`db_open`](database.md#db_open), [`db_pool`](database.md#db_pool), [`db_exec`](database.md#db_exec), [`db_query`](database.md#db_query), [`db_next`](database.md#db_next), [`db_int`](database.md#db_int), [`db_float`](database.md#db_float), [`db_string`](database.md#db_string), [`db_is_null`](database.md#db_is_null), [`db_json`](database.md#db_json), [`db_all`](database.md#db_all), [`db_one`](database.md#db_one), [`db_last_id`](database.md#db_last_id), [`db_error`](database.md#db_error)

## [Errors](errors.md)

[`error`](errors.md#error)

## [Tasks (go / await)](tasks.md)

[`sleep_ms`](tasks.md#sleep_ms), [`await_all`](tasks.md#await_all), [`await_timeout`](tasks.md#await_timeout)

## [Hub (messages between requests)](hub.md)

[`hub_publish`](hub.md#hub_publish), [`hub_subscribe`](hub.md#hub_subscribe), [`hub_resume`](hub.md#hub_resume), [`hub_next`](hub.md#hub_next), [`hub_last_id`](hub.md#hub_last_id)

## [Other servers and programs](client.md)

[`http_get`](client.md#http_get), [`http_post`](client.md#http_post), [`http_stream`](client.md#http_stream), [`stream_next`](client.md#stream_next), [`stream_last_id`](client.md#stream_last_id), [`read_line`](client.md#read_line), [`run`](client.md#run)

## [Security (hashes, passwords, random)](security.md)

[`env`](security.md#env), [`hash`](security.md#hash), [`hash_hmac`](security.md#hash_hmac), [`hash_equals`](security.md#hash_equals), [`random_token`](security.md#random_token), [`random_int`](security.md#random_int), [`password_hash`](security.md#password_hash), [`password_verify`](security.md#password_verify)
