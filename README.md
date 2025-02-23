# py-posix_tz

Python / MicroPython package for processing POSIX TZ names/rules for localtime() lookup/derivation that's timezone and DST aware

https://github.com/clach04/py-posix_tz

Primarily focused on MicroPython where memory/storage is restricted. If you have a full Python implementation (like CPython, etc.) use an IANA timezone API instead.

The timezone support that POSIX TZ offers (in general, not specifically about this package) is limited to now and the future. It has no idea about previous rules, there is only one rule. If new rules for a timezone are created, a new TZ will need to be created and deployed.

## Resources

### Documentation on rules

  * https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
  * https://www.netburner.com/learn/time-zones-and-daylight-savings-with-olson-and-posix/
  * Posix specification for time zone names: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap08.html#tag_08_03
  * https://developer.ibm.com/articles/au-aix-posix/#posix-format-specification1


### Sample mappings IANA names to posix strings

  * https://github.com/clach04/Esp8266_Wifi_Matrix_Clock/blob/patch-1/posix.md#sample-iana-to-posix-strings (from https://github.com/yuan910715/Esp8266_Wifi_Matrix_Clock/blob/master/posix.md)
  * https://support.cyberdata.net/portal/en/kb/articles/010d63c0cfce3676151e1f2d5442e311
