## Project

### Folder naming

Lowercased and separated by _

## Political Administrative Levels  

To allow us to sort and filter entities we've set a 4 level classification (same than google places adress_components geocode response)

Political Administrative Levels `PAL` will be the following ones:
- country used as `country` `short` and allways using the abbreviation.
- administrative_area_level_1 used as `aal1` `long`
- administrative_area_level_2 used as `aal2` `long`
- locality used as `locality` `long`

View more: https://developers.google.com/maps/documentation/geocoding/overview#Types

# Language codes
https://developers.google.com/maps/faq#languagesupport

# Countries
https://en.wikipedia.org/wiki/Country_code_top-level_domain
https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Country_code_top-level_domains
https://www.iana.org/domains/root/db

# Standarizations

+ Language subtags: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
+ https://www.gs1.org/standards/gpc/jun-2019
+ https://tools.ietf.org/html/rfc7946#section-3.1.8
+ https://geojson.org/
+ https://es.wikipedia.org/wiki/Anexo:Municipios_de_Espa%C3%B1a_por_poblaci%C3%B3n
+ https://emilyriederer.netlify.app/post/column-name-contracts/

# LanguageCodes vs Country

They should co-habitate. The user interface should be multilingual and it's not related to the country. I can visit `ES` page with the `en` language as I can visit `FR` platform in `es`.