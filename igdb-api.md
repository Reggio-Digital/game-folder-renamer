# IGDB API Documentation

## Getting Started

### Prerequisites

In order to use the IGDB API, you must have a Twitch Account.

### Setup Steps

1. **Sign Up with Twitch** for a free account
2. **Enable Two Factor Authentication** on your Twitch account
3. **Register your application** in the Twitch Developer Portal
   - The OAuth Redirect URL field is not used by IGDB. Please add `localhost` to continue.
   - The Client Type must be set to **Confidential** to generate Client Secrets
4. **Manage your newly created application**
5. **Generate a Client Secret** by pressing [New Secret]
6. **Take note of the Client ID and Client Secret**

## Authentication

Now that you have a Client ID and Client Secret, you will be authenticating as a Twitch Developer using OAuth2.

Detailed information can be found in the [Twitch Developer Docs](https://dev.twitch.tv/docs/authentication).

### Getting an Access Token

Make a POST request to `https://id.twitch.tv/oauth2/token` with the following query string parameters:

```
client_id=<Your Client ID>
client_secret=<Your Client Secret>
grant_type=client_credentials
```

#### Example Request

If your Client ID is `abcdefg12345` and your Client Secret is `hijklmn67890`, the complete URL would be:

```
POST: https://id.twitch.tv/oauth2/token?client_id=abcdefg12345&client_secret=hijklmn67890&grant_type=client_credentials
```

#### Example Response

The response will be a JSON object containing the access token and expiration time:

```json
{
  "access_token": "access12345token",
  "expires_in": 5587808,
  "token_type": "bearer"
}
```

> **Note:** The `expires_in` field shows the number of seconds before the access_token will expire and must be refreshed.

## Making Requests

### Request Configuration

- **Method**: Most API requests use the `POST` method
- **Base URL**: `https://api.igdb.com/v4`
- **Endpoint**: Append `/{endpoint_name}` to the base URL (e.g., `https://api.igdb.com/v4/games`)

### Required Headers

Include your Client ID and Access Token in the request headers:

```
Client-ID: <Your Client ID>
Authorization: Bearer <Your Access Token>
```

> **Important:** Take special care with capitalization. `Bearer` should be hard-coded in front of your access_token.

### Request Body

Use the request body to specify:
- Fields you want to retrieve
- Filters
- Sorting options
- Other query parameters

#### Example Request

If your Client ID is `abcdefg12345` and your access_token is `access12345token`:

```
POST: https://api.igdb.com/v4/games
Client-ID: abcdefg12345
Authorization: Bearer access12345token
Body: "fields *;"
```

> **Note:** If you are trying to make requests via the browser, you will run into CORS errors as the API does not allow requests directly from browsers. See the CORS Proxy section for workarounds.

## Rate Limits

- **Request Rate**: 4 requests per second maximum
  - Exceeding this limit returns a `429 Too Many Requests` response
- **Concurrent Requests**: Up to 8 open requests at any moment
  - This can occur if requests take longer than 1 second to respond when multiple requests are being made

## Client Libraries & Wrappers

Get setup quickly by using one of these wrappers!

### Official Apicalypse Libraries

- [NodeJS](https://github.com/igdb/node-igdb)
- [JVM/Kotlin/Java](https://github.com/husnjak/IGDB-API-JVM)
- [Swift](https://github.com/husnjak/IGDB-API-SWIFT)
- [Python](https://github.com/twitchtv/igdb-api-python)

### Third Party Libraries

- [PHP/Laravel](https://github.com/messerli90/igdb-laravel)
- [GO](https://github.com/Henry-Sarabia/igdb)
- [Ruby](https://github.com/ahmetabdi/igdb)
- [C#/.NET](https://github.com/kamranayub/igdb-dotnet)
- [Deno](https://github.com/MattIPv4/igdb-deno)

### Additional Resources

- [OpenAPI Documentation](https://api-docs.igdb.com/)
- [Postman Collection](https://www.postman.com/igdb/workspace/igdb-api/overview)

## Query Examples

> **Tip:** It's recommended to try out your queries in an API viewer like Postman or Insomnia before using code. This helps you find problems a lot sooner!
>
> See the [Postman setup example](link) for guidance.

### Basic Queries

#### Get names of 10 games

```
POST: https://api.igdb.com/v4/games/
Body: fields name; limit 10;
```

#### Get all information from a specific game

Get all data for game with ID 1942:

```
POST: https://api.igdb.com/v4/games/
Body: fields *; where id = 1942;
```

#### Exclude specific fields from results

Remove `alternative_name` from your result query:

```
POST: https://api.igdb.com/v4/platforms/
Body: fields *; exclude alternative_name;
```

### Filtering Queries

#### Get all games from specific genres

```
POST: https://api.igdb.com/v4/genres/
Body: fields *; where id = (8,9,11);
```

> **Note:** You can comma-separate multiple IDs (8, 9, and 11). When you have multiple IDs, they must be surrounded by parentheses. Single IDs can be queried with or without parentheses.

#### Count games with rating higher than 75

```
POST: https://api.igdb.com/v4/games/count
Body: where rating > 75;
```

#### Order results by rating

```
POST: https://api.igdb.com/v4/games/
Body: fields name,rating; sort rating desc;
```

### Platform-Specific Queries

#### Coming soon games for PlayStation 4

```
POST: https://api.igdb.com/v4/release_dates/
Body: fields *; where game.platforms = 48 & date > 1538129354; sort date asc;
```

> **Note:**
> - `1538129354` is the timestamp in milliseconds for 28/09/2018 (you need to generate this yourself)
> - `48` is the platform ID for PlayStation 4

#### Recently released games for PlayStation 4

```
POST: https://api.igdb.com/v4/release_dates/
Body: fields *; where game.platforms = 48 & date < 1538129354; sort date desc;
```

> **Note:** You can use `&` (AND) or `|` (OR) to combine filters to better define query behavior.

#### Get PlayStation 4 exclusives

```
POST: https://api.igdb.com/v4/games/
Body: fields name,category,platforms; where category = 0 & platforms = 48;
```

#### Get games released only on PlayStation 4 AND PC

```
POST: https://api.igdb.com/v4/games/
Body: fields name,category,platforms; where category = 0 & platforms = {48,6};
```

### Search Queries

#### Search and return specific fields

```
POST: https://api.igdb.com/v4/games/
Body: search "Halo"; fields name,release_date.human;
```

Or with different fields:

```
POST: https://api.igdb.com/v4/games/
Body: fields name, involved_companies; search "Halo";
```

#### Search games but exclude versions (editions)

```
POST: https://api.igdb.com/v4/games/
Body: fields name, involved_companies; search "Assassins Creed"; where version_parent = null;
```

This will return search results with ID and name of the game but exclude editions such as "Collectors Edition".

#### Search across all endpoints

```
POST: https://api.igdb.com/v4/search
Body: fields *; search "sonic the hedgehog"; limit 50;
```

> **Note:** Search is now also its own endpoint. Search is usable on: Characters, Collections, Games, Platforms, and Themes.
>
> The example above searches for "Sonic the Hedgehog" which will find the Character Sonic, the collection Sonic the Hedgehog, and several games with names containing Sonic the Hedgehog.

### Version Queries

#### Get versions (editions) of a game

```
POST: https://api.igdb.com/v4/game_versions/
Body: fields game.name,games.name; where game = 28540;
```

The resulting object will contain all games that are a version of the game with ID 28540.

#### Get the parent game for a version

```
POST: https://api.igdb.com/v4/games/
Body: fields version_parent.*; where id = 39047;
```

The resulting object will contain all main games.

---

## API Endpoints

### Age Rating

Age Rating according to various rating organisations.

**Endpoint:** `https://api.igdb.com/v4/age_ratings`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/age_ratings',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields category,checksum,content_descriptions,organization,rating,rating_category,rating_content_descriptions,rating_cover_url,synopsis;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** Use `organization` instead |
| checksum | uuid | Hash of the object |
| content_descriptions | Array of Age Rating Content Description IDs | |
| organization | Reference ID for Age Rating Organization | The organization that has issued a specific rating |
| rating | Rating Enum | **DEPRECATED!** Use `rating_category` instead |
| rating_category | Reference ID for Age Rating Category | The category of a rating |
| rating_content_descriptions | Array of Age Rating Content Description V2 IDs | The rating content descriptions |
| rating_cover_url | String | The URL for the image of an age rating |
| synopsis | String | A free text motivating a rating |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `organization` instead
> - `rating`: DEPRECATED! Use `rating_category` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| ESRB | 1 |
| PEGI | 2 |
| CERO | 3 |
| USK | 4 |
| GRAC | 5 |
| CLASS_IND | 6 |
| ACB | 7 |

**Rating Enum**

| Name | Value |
|------|-------|
| Three | 1 |
| Seven | 2 |
| Twelve | 3 |
| Sixteen | 4 |
| Eighteen | 5 |
| RP | 6 |
| EC | 7 |
| E | 8 |
| E10 | 9 |
| T | 10 |
| M | 11 |
| AO | 12 |
| CERO_A | 13 |
| CERO_B | 14 |
| CERO_C | 15 |
| CERO_D | 16 |
| CERO_Z | 17 |
| USK_0 | 18 |
| USK_6 | 19 |
| USK_12 | 20 |
| USK_16 | 21 |
| USK_18 | 22 |
| GRAC_ALL | 23 |
| GRAC_Twelve | 24 |
| GRAC_Fifteen | 25 |
| GRAC_Eighteen | 26 |
| GRAC_TESTING | 27 |
| CLASS_IND_L | 28 |
| CLASS_IND_Ten | 29 |
| CLASS_IND_Twelve | 30 |
| CLASS_IND_Fourteen | 31 |
| CLASS_IND_Sixteen | 32 |
| CLASS_IND_Eighteen | 33 |
| ACB_G | 34 |
| ACB_PG | 35 |
| ACB_M | 36 |
| ACB_MA15 | 37 |
| ACB_R18 | 38 |
| ACB_RC | 39 |

---

### Age Rating Category

The rating category from the organization.

**Endpoint:** `https://api.igdb.com/v4/age_rating_categories`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/age_rating_categories',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields checksum,created_at,organization,rating,updated_at;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| organization | Reference ID for Age Rating Organization | The rating organization |
| rating | String | The rating name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Age Rating Content Description

> **DEPRECATED!** Use `age_rating_content_descriptions_v2` instead.

**Endpoint:** `https://api.igdb.com/v4/age_rating_content_descriptions`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/age_rating_content_descriptions',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields category,checksum,description;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** |
| checksum | uuid | Hash of the object |
| description | String | |

#### Enums

**Category Enum**

| Name | Value | Name | Value |
|------|-------|------|-------|
| ESRB_alcohol_reference | 1 | ESRB_mild_sexual themes | 44 |
| ESRB_animated_blood | 2 | ESRB_use_of alcohol and tobacco | 45 |
| ESRB_blood | 3 | ESRB_animated_blood and gore | 46 |
| ESRB_blood_and gore | 4 | ESRB_mild_fantasy violence | 47 |
| ESRB_cartoon_violence | 5 | ESRB_mild_lyrics | 48 |
| ESRB_comic_mischief | 6 | ESRB_realistic_blood | 49 |
| ESRB_crude_humor | 7 | PEGI_violence | 50 |
| ESRB_drug_reference | 8 | PEGI_sex | 51 |
| ESRB_fantasy_violence | 9 | PEGI_drugs | 52 |
| ESRB_intense_violence | 10 | PEGI_fear | 53 |
| ESRB_language | 11 | PEGI_discrimination | 54 |
| ESRB_lyrics | 12 | PEGI_bad_language | 55 |
| ESRB_mature_humor | 13 | PEGI_gambling | 56 |
| ESRB_nudity | 14 | PEGI_online_gameplay | 57 |
| ESRB_partial_nudity | 15 | PEGI_in_game_purchases | 58 |
| ESRB_real_gambling | 16 | CERO_love | 59 |
| ESRB_sexual_content | 17 | CERO_sexual_content | 60 |
| ESRB_sexual_themes | 18 | CERO_violence | 61 |
| ESRB_sexual_violence | 19 | CERO_horror | 62 |
| ESRB_simulated_gambling | 20 | CERO_drinking_smoking | 63 |
| ESRB_strong_language | 21 | CERO_gambling | 64 |
| ESRB_strong_lyrics | 22 | CERO_crime | 65 |
| ESRB_strong_sexual content | 23 | CERO_controlled_substances | 66 |
| ESRB_suggestive_themes | 24 | CERO_languages_and others | 67 |
| ESRB_tobacco_reference | 25 | GRAC_sexuality | 68 |
| ESRB_use_of alcohol | 26 | GRAC_violence | 69 |
| ESRB_use_of drugs | 27 | GRAC_fear_horror_threatening | 70 |
| ESRB_use_of tobacco | 28 | GRAC_language | 71 |
| ESRB_violence | 29 | GRAC_alcohol_tobacco_drug | 72 |
| ESRB_violent_references | 30 | GRAC_crime_anti_social | 73 |
| ESRB_animated_violence | 31 | GRAC_gambling | 74 |
| ESRB_mild_language | 32 | CLASS_IND_violencia | 75 |
| ESRB_mild_violence | 33 | CLASS_IND_violencia_extrema | 76 |
| ESRB_use_of drugs and alcohol | 34 | CLASS_IND_conteudo_sexual | 77 |
| ESRB_drug_and alcohol reference | 35 | CLASS_IND_nudez | 78 |
| ESRB_mild_suggestive themes | 36 | CLASS_IND_sexo | 79 |
| ESRB_mild_cartoon violence | 37 | CLASS_IND_sexo_explicito | 80 |
| ESRB_mild_blood | 38 | CLASS_IND_drogas | 81 |
| ESRB_realistic_blood and gore | 39 | CLASS_IND_drogas_licitas | 82 |
| ESRB_realistic_violence | 40 | CLASS_IND_drogas_ilicitas | 83 |
| ESRB_alcohol_and tobacco reference | 41 | CLASS_IND_linguagem_impropria | 84 |
| ESRB_mature_sexual themes | 42 | CLASS_IND_atos_criminosos | 85 |
| ESRB_mild_animated violence | 43 | | |

---

### Age Rating Content Description Type

Age Rating Content Description Types.

**Endpoint:** `https://api.igdb.com/v4/age_rating_content_description_types`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/age_rating_content_description_types',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields checksum,created_at,name,slug,updated_at;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Age Rating Content Description V2

Age Rating Content Descriptions.

**Endpoint:** `https://api.igdb.com/v4/age_rating_content_descriptions_v2`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/age_rating_content_descriptions_v2',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields checksum,created_at,description,description_type,organization,updated_at;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | |
| description_type | Reference ID for Age Rating Content Description Type | The age rating content description type |
| organization | Reference ID for Age Rating Organization | The rating organization |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Age Rating Organization

Age Rating according to various rating organisations.

**Endpoint:** `https://api.igdb.com/v4/age_rating_organizations`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/age_rating_organizations',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields checksum,created_at,name,updated_at;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | The title of an age rating organization |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Artwork

Official artworks (resolution and aspect ratio may vary).

**Endpoint:** `https://api.igdb.com/v4/artworks`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/artworks',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields alpha_channel,animated,artwork_type,checksum,game,height,image_id,url,width;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| artwork_type | Reference ID for Artwork Type | The artwork type |
| checksum | uuid | Hash of the object |
| game | Reference ID for Game | The game this artwork is associated with |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Alternative Name

Alternative and international game titles.

**Endpoint:** `https://api.igdb.com/v4/alternative_names`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/alternative_names',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields checksum,comment,game,name;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| comment | String | A description of what kind of alternative name it is (Acronym, Working title, Japanese title etc) |
| game | Reference ID for Game | The game this alternative name is associated with |
| name | String | An alternative name |

---

### Artwork Type

Artwork Types.

**Endpoint:** `https://api.igdb.com/v4/artwork_types`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/artwork_types',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields checksum,created_at,name,slug,updated_at;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Character

Video game characters.

**Endpoint:** `https://api.igdb.com/v4/characters`

#### Example Request

```python
from requests import post

response = post(
    'https://api.igdb.com/v4/characters',
    headers={
        'Client-ID': 'Your Client ID',
        'Authorization': 'Bearer Your Access Token'
    },
    data='fields akas,character_gender,character_species,checksum,country_name,created_at,description,games,gender,mug_shot,name,slug,species,updated_at,url;'
)
print("response: %s" % str(response.json()))
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| akas | Array of Strings | Alternative names for a character |
| character_gender | Reference ID for Character Gender | |
| character_species | Reference ID for Character Specie | |
| checksum | uuid | Hash of the object |
| country_name | String | A characters country of origin |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | A text describing a character |
| games | Array of Game IDs | |
| gender | Gender Enum | **DEPRECATED!** Use `character_gender` instead |
| mug_shot | Reference ID for Character Mug Shot | An image depicting a character |
| name | String | |
| slug | String | A url-safe, unique, lower-case version of the name |
| species | Species Enum | **DEPRECATED!** Use `character_species` instead |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

> **Deprecated Fields:**
> - `gender`: DEPRECATED! Use `character_gender` instead
> - `species`: DEPRECATED! Use `character_species` instead

#### Enums

**Gender Enum**

| Name | Value |
|------|-------|
| Male | 0 |
| Female | 1 |
| Other | 2 |

**Species Enum**

| Name | Value |
|------|-------|
| Human | 1 |
| Alien | 2 |
| Animal | 3 |
| Android | 4 |
| Unknown | 5 |

---

### Character Gender

**Endpoint:** `https://api.igdb.com/v4/character_genders`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Character Mug Shot

Images depicting game characters.

**Endpoint:** `https://api.igdb.com/v4/character_mug_shots`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| checksum | uuid | Hash of the object |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Character Species

**Endpoint:** `https://api.igdb.com/v4/character_species`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Collection

Game collections (series).

**Endpoint:** `https://api.igdb.com/v4/collections`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| as_child_relations | Array of Collection Relation IDs | |
| as_parent_relations | Array of Collection Relation IDs | |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| games | Array of Game IDs | The games that are associated with this collection |
| name | String | Umbrella term for a collection of games |
| slug | String | A url-safe, unique, lower-case version of the name |
| type | Reference ID for Collection Type | The type of collection |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Collection Membership

**Endpoint:** `https://api.igdb.com/v4/collection_memberships`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| collection | Reference ID for Collection | The collection that is associated with this membership |
| created_at | datetime | Date this was initially added to the IGDB database |
| game | Reference ID for Game | The game that is associated with this membership |
| type | Reference ID for Collection Membership Type | The Collection Membership Type |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Collection Membership Type

**Endpoint:** `https://api.igdb.com/v4/collection_membership_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| allowed_collection_type | Reference ID for Collection Type | The allowed collection type |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | Description of the membership type |
| name | String | The membership type name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Collection Relation

Describes relationships between collections.

**Endpoint:** `https://api.igdb.com/v4/collection_relations`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| child_collection | Reference ID for Collection | The child collection of this collection |
| created_at | datetime | Date this was initially added to the IGDB database |
| parent_collection | Reference ID for Collection | The parent collection of this collection |
| type | Reference ID for Collection Relation Type | The collection relationship type |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Collection Relation Type

**Endpoint:** `https://api.igdb.com/v4/collection_relation_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| allowed_child_type | Reference ID for Collection Type | The allowed child collection type |
| allowed_parent_type | Reference ID for Collection Type | The allowed parent collection type |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | The relationship type description |
| name | String | The relationship type name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Collection Type

**Endpoint:** `https://api.igdb.com/v4/collection_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | Description of the collection type |
| name | String | The name of the collection type |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Company

Video game companies (publishers and developers).

**Endpoint:** `https://api.igdb.com/v4/companies`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| change_date | Unix Time Stamp | The date when a company got a new ID |
| change_date_category | Change Date Category Enum | **DEPRECATED!** Use `change_date_format` instead |
| change_date_format | Reference ID for Date Format | The format of the change date |
| changed_company_id | Reference ID for Company | The new ID for a company that has gone through a merger or restructuring |
| checksum | uuid | Hash of the object |
| country | Integer | ISO 3166-1 country code |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | A free text description of a company |
| developed | Array of Game IDs | An array of games that a company has developed |
| logo | Reference ID for Company Logo | The company's logo |
| name | String | |
| parent | Reference ID for Company | A company with a controlling interest in a specific company |
| published | Array of Game IDs | An array of games that a company has published |
| slug | String | A url-safe, unique, lower-case version of the name |
| start_date | Unix Time Stamp | The date a company was founded |
| start_date_category | Start Date Category Enum | **DEPRECATED!** Use `start_date_format` instead |
| start_date_format | Reference ID for Date Format | The format of the start date |
| status | Reference ID for Company Status | The status of the company |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |
| websites | Array of Company Website IDs | The companies official websites |

> **Deprecated Fields:**
> - `change_date_category`: DEPRECATED! Use `change_date_format` instead
> - `start_date_category`: DEPRECATED! Use `start_date_format` instead

#### Enums

**Change Date Category Enum**

| Name | Value |
|------|-------|
| YYYYMMMMDD | 0 |
| YYYYMMMM | 1 |
| YYYY | 2 |
| YYYYQ1 | 3 |
| YYYYQ2 | 4 |
| YYYYQ3 | 5 |
| YYYYQ4 | 6 |
| TBD | 7 |

**Start Date Category Enum**

| Name | Value |
|------|-------|
| YYYYMMMMDD | 0 |
| YYYYMMMM | 1 |
| YYYY | 2 |
| YYYYQ1 | 3 |
| YYYYQ2 | 4 |
| YYYYQ3 | 5 |
| YYYYQ4 | 6 |
| TBD | 7 |

---

### Company Logo

Company logos (developers and publishers).

**Endpoint:** `https://api.igdb.com/v4/company_logos`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| checksum | uuid | Hash of the object |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Company Status

**Endpoint:** `https://api.igdb.com/v4/company_statuses`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Company Website

**Endpoint:** `https://api.igdb.com/v4/company_websites`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** Use `type` instead |
| checksum | uuid | Hash of the object |
| trusted | boolean | |
| type | Reference ID for Website Type | The website type associated with the website |
| url | String | The website address (URL) of the item |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `type` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| official | 1 |
| wikia | 2 |
| wikipedia | 3 |
| facebook | 4 |
| twitter | 5 |
| twitch | 6 |
| instagram | 8 |
| youtube | 9 |
| iphone | 10 |
| ipad | 11 |
| android | 12 |
| steam | 13 |
| reddit | 14 |
| itch | 15 |
| epicgames | 16 |
| gog | 17 |
| discord | 18 |
| bluesky | 19 |

---

### Cover

Game cover art.

**Endpoint:** `https://api.igdb.com/v4/covers`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| checksum | uuid | Hash of the object |
| game | Reference ID for Game | The game this cover is associated with. If empty, this cover belongs to a game_localization |
| game_localization | Reference ID for Game Localization | The game localization this cover might be associated with |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Date Format

**Endpoint:** `https://api.igdb.com/v4/date_formats`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| format | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Event

Gaming events (e.g., GamesCom, Tokyo Game Show, PAX, GSL).

**Endpoint:** `https://api.igdb.com/v4/events`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | The description of the event |
| end_time | datetime | End time of the event in UTC |
| event_logo | Reference ID for Event Logo | Logo of the event |
| event_networks | Array of Event Network IDs | URLs associated with the event |
| games | Array of Game IDs | Games featured in the event |
| live_stream_url | String | URL to the livestream of the event |
| name | String | The name of the event |
| slug | String | A url-safe, unique, lower-case version of the name |
| start_time | datetime | Start time of the event in UTC |
| time_zone | String | Timezone the event is in |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| videos | Array of Game Video IDs | Trailers featured in the event |

---

### Event Logo

**Endpoint:** `https://api.igdb.com/v4/event_logos`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| event | Reference ID for Event | The event associated with this logo |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Event Network

URLs related to events (e.g., Twitter, Facebook, YouTube).

**Endpoint:** `https://api.igdb.com/v4/event_networks`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| event | Reference ID for Event | The event associated with this URL |
| network_type | Reference ID for Network Type | Network type |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### External Game

Game IDs on other services.

**Endpoint:** `https://api.igdb.com/v4/external_games`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** Use `external_game_source` instead |
| checksum | uuid | Hash of the object |
| countries | Array of Integers | The ISO country code of the external game product |
| created_at | datetime | Date this was initially added to the IGDB database |
| external_game_source | Reference ID for External Game Source | The source of the external game |
| game | Reference ID for Game | The IGDB ID of the game |
| game_release_format | Reference ID for Game Release Format | The release format of the external game |
| media | Media Enum | **DEPRECATED!** Use `game_release_format` instead |
| name | String | The name of the game according to the other service |
| platform | Reference ID for Platform | The platform of the external game product |
| uid | String | The other service's ID for this game |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |
| year | Integer | The year in full (e.g., 2018) |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `external_game_source` instead
> - `media`: DEPRECATED! Use `game_release_format` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| steam | 1 |
| gog | 5 |
| youtube | 10 |
| microsoft | 11 |
| apple | 13 |
| twitch | 14 |
| android | 15 |
| amazon_asin | 20 |
| amazon_luna | 22 |
| amazon_adg | 23 |
| epic_game_store | 26 |
| oculus | 28 |
| utomik | 29 |
| itch_io | 30 |
| xbox_marketplace | 31 |
| kartridge | 32 |
| playstation_store_us | 36 |
| focus_entertainment | 37 |
| xbox_game_pass_ultimate_cloud | 54 |
| gamejolt | 55 |

**Media Enum**

| Name | Value |
|------|-------|
| digital | 1 |
| physical | 2 |

---

### External Game Source

**Endpoint:** `https://api.igdb.com/v4/external_game_sources`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Franchise

Video game franchises (e.g., Star Wars).

**Endpoint:** `https://api.igdb.com/v4/franchises`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| games | Array of Game IDs | The games that are associated with this franchise |
| name | String | The name of the franchise |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---
### Game

Video games.

**Endpoint:** `https://api.igdb.com/v4/games`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| age_ratings | Array of Age Rating IDs | The PEGI rating |
| aggregated_rating | Double | Rating based on external critic scores |
| aggregated_rating_count | Integer | Number of external critic scores |
| alternative_names | Array of Alternative Name IDs | Alternative names for this game |
| artworks | Array of Artwork IDs | Artworks of this game |
| bundles | Array of Game IDs | The bundles this game is a part of |
| category | Category Enum | **DEPRECATED!** Use `game_type` instead |
| checksum | uuid | Hash of the object |
| collection | Reference ID for Collection | **DEPRECATED!** Use `collections` instead |
| collections | Array of Collection IDs | The collections that this game is in |
| cover | Reference ID for Cover | The cover of this game |
| created_at | datetime | Date this was initially added to the IGDB database |
| dlcs | Array of Game IDs | DLCs for this game |
| expanded_games | Array of Game IDs | Expanded games of this game |
| expansions | Array of Game IDs | Expansions of this game |
| external_games | Array of External Game IDs | External IDs this game has on other services |
| first_release_date | Unix Time Stamp | The first release date for this game |
| follows | Integer | **DEPRECATED!** - To be removed |
| forks | Array of Game IDs | Forks of this game |
| franchise | Reference ID for Franchise | The main franchise |
| franchises | Array of Franchise IDs | Other franchises the game belongs to |
| game_engines | Array of Game Engine IDs | The game engine used in this game |
| game_localizations | Array of Game Localization IDs | Supported game localizations for this game |
| game_modes | Array of Game Mode IDs | Modes of gameplay |
| game_status | Reference ID for Game Status | The status of the games release |
| game_type | Reference ID for Game Type | The type of game |
| genres | Array of Genre IDs | Genres of the game |
| hypes | Integer | Number of follows a game gets before release |
| involved_companies | Array of Involved Company IDs | Companies who developed this game |
| keywords | Array of Keyword IDs | Associated keywords |
| language_supports | Array of Language Support IDs | Supported languages for this game |
| multiplayer_modes | Array of Multiplayer Mode IDs | Multiplayer modes for this game |
| name | String | |
| parent_game | Reference ID for Game | If a DLC, expansion or part of a bundle, this is the main game or bundle |
| platforms | Array of Platform IDs | Platforms this game was released on |
| player_perspectives | Array of Player Perspective IDs | The main perspective of the player |
| ports | Array of Game IDs | Ports of this game |
| rating | Double | Average IGDB user rating |
| rating_count | Integer | Total number of IGDB user ratings |
| release_dates | Array of Release Date IDs | Release dates of this game |
| remakes | Array of Game IDs | Remakes of this game |
| remasters | Array of Game IDs | Remasters of this game |
| screenshots | Array of Screenshot IDs | Screenshots of this game |
| similar_games | Array of Game IDs | Similar games |
| slug | String | A url-safe, unique, lower-case version of the name |
| standalone_expansions | Array of Game IDs | Standalone expansions of this game |
| status | Status Enum | **DEPRECATED!** Use `game_status` instead |
| storyline | String | A short description of a games story |
| summary | String | A description of the game |
| tags | Array of Tag Numbers | Related entities in the IGDB API |
| themes | Array of Theme IDs | Themes of the game |
| total_rating | Double | Average rating based on both IGDB user and external critic scores |
| total_rating_count | Integer | Total number of user and external critic scores |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |
| version_parent | Reference ID for Game | If a version, this is the main game |
| version_title | String | Title of this version (e.g., Gold edition) |
| videos | Array of Game Video IDs | Videos of this game |
| websites | Array of Website IDs | Websites associated with this game |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `game_type` instead
> - `collection`: DEPRECATED! Use `collections` instead
> - `follows`: DEPRECATED! - To be removed
> - `status`: DEPRECATED! Use `game_status` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| main_game | 0 |
| dlc_addon | 1 |
| expansion | 2 |
| bundle | 3 |
| standalone_expansion | 4 |
| mod | 5 |
| episode | 6 |
| season | 7 |
| remake | 8 |
| remaster | 9 |
| expanded_game | 10 |
| port | 11 |
| fork | 12 |
| pack | 13 |
| update | 14 |

**Status Enum**

| Name | Value |
|------|-------|
| released | 0 |
| alpha | 2 |
| beta | 3 |
| early_access | 4 |
| offline | 5 |
| cancelled | 6 |
| rumored | 7 |
| delisted | 8 |

---

### Game Engine

Video game engines (e.g., Unreal Engine).

**Endpoint:** `https://api.igdb.com/v4/game_engines`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| companies | Array of Company IDs | Companies who used this game engine |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | Description of the game engine |
| logo | Reference ID for Game Engine Logo | Logo of the game engine |
| name | String | Name of the game engine |
| platforms | Array of Platform IDs | Platforms this game engine was deployed on |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Game Engine Logo

**Endpoint:** `https://api.igdb.com/v4/game_engine_logos`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| checksum | uuid | Hash of the object |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Game Localization

**Endpoint:** `https://api.igdb.com/v4/game_localizations`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| cover | Reference ID for Cover | The cover of this game localization |
| created_at | datetime | Date this was initially added to the IGDB database |
| game | Reference ID for Game | The game the localization belongs to |
| name | String | |
| region | Reference ID for Region | The region of the localization |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Game Mode

Game modes (e.g., Single player, Multiplayer).

**Endpoint:** `https://api.igdb.com/v4/game_modes`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | The name of the game mode |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Game Release Format

**Endpoint:** `https://api.igdb.com/v4/game_release_formats`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| format | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Game Status

**Endpoint:** `https://api.igdb.com/v4/game_statuses`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| status | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Game Time To Beat

Average time to beat times for a game.

**Endpoint:** `https://api.igdb.com/v4/game_time_to_beats`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| completely | Integer | Average time (in seconds) to finish the game to 100% completion |
| count | Integer | Total number of time to beat submissions for this game |
| created_at | datetime | Date this was initially added to the IGDB database |
| game_id | Integer | The ID of the game associated with the time to beat data |
| hastily | Integer | Average time (in seconds) to finish the game to its credits without extras |
| normally | Integer | Average time (in seconds) to finish the game while mixing in some extras |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Game Type

**Endpoint:** `https://api.igdb.com/v4/game_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| type | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Game Version

Details about game editions and versions.

**Endpoint:** `https://api.igdb.com/v4/game_versions`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| features | Array of Game Version Feature IDs | Features that make each version/edition different |
| game | Reference ID for Game | The game these versions/editions are of |
| games | Array of Game IDs | Game versions and editions |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Game Version Feature

Features and descriptions of what makes each version/edition different.

**Endpoint:** `https://api.igdb.com/v4/game_version_features`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | The category of the feature description |
| checksum | uuid | Hash of the object |
| description | String | The description of the feature |
| position | Integer | Position of this feature in the list of features |
| title | String | The title of the feature |
| values | Array of Game Version Feature Value IDs | The bool/text value of the feature |

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| boolean | 0 |
| description | 1 |

---

### Game Version Feature Value

**Endpoint:** `https://api.igdb.com/v4/game_version_feature_values`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| game | Reference ID for Game | The version/edition this value refers to |
| game_feature | Reference ID for Game Version Feature | The ID of the game feature |
| included_feature | Included Feature Enum | The boolean value of this feature |
| note | String | The text value of this feature |

#### Enums

**Included Feature Enum**

| Name | Value |
|------|-------|
| NOT_INCLUDED | 0 |
| INCLUDED | 1 |
| PRE_ORDER_ONLY | 2 |

---

### Game Video

Videos associated with games.

**Endpoint:** `https://api.igdb.com/v4/game_videos`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| game | Reference ID for Game | The game this video is associated with |
| name | String | The name of the video |
| video_id | String | The external ID of the video (YouTube links) |

---

### Genre

Video game genres.

**Endpoint:** `https://api.igdb.com/v4/genres`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Involved Company

**Endpoint:** `https://api.igdb.com/v4/involved_companies`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| company | Reference ID for Company | The company involved |
| created_at | datetime | Date this was initially added to the IGDB database |
| developer | Boolean | Whether the company developed the game |
| game | Reference ID for Game | The game this company was involved with |
| porting | Boolean | Whether the company ported the game |
| publisher | Boolean | Whether the company published the game |
| supporting | Boolean | Whether the company supported the game |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Keyword

Keywords tagged to games (e.g., "world war 2", "steampunk").

**Endpoint:** `https://api.igdb.com/v4/keywords`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Language

Languages used in the Language Support endpoint.

**Endpoint:** `https://api.igdb.com/v4/languages`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| locale | String | The combination of language code and country code |
| name | String | The English name of the language |
| native_name | String | The native name of the language |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Language Support

Different language options for games (voice acting, subtitles, interface).

**Endpoint:** `https://api.igdb.com/v4/language_supports`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| game | Reference ID for Game | |
| language | Reference ID for Language | |
| language_support_type | Reference ID for Language Support Type | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Language Support Type

**Endpoint:** `https://api.igdb.com/v4/language_support_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Multiplayer Mode

Supported multiplayer types for games.

**Endpoint:** `https://api.igdb.com/v4/multiplayer_modes`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| campaigncoop | boolean | True if the game supports campaign coop |
| checksum | uuid | Hash of the object |
| dropin | boolean | True if the game supports drop in/out multiplayer |
| game | Reference ID for Game | The game this multiplayer mode is associated with |
| lancoop | boolean | True if the game supports LAN coop |
| offlinecoop | boolean | True if the game supports offline coop |
| offlinecoopmax | Integer | Maximum number of offline players in offline coop |
| offlinemax | Integer | Maximum number of players in offline multiplayer |
| onlinecoop | boolean | True if the game supports online coop |
| onlinecoopmax | Integer | Maximum number of online players in online coop |
| onlinemax | Integer | Maximum number of players in online multiplayer |
| platform | Reference ID for Platform | The platform this multiplayer mode refers to |
| splitscreen | boolean | True if the game supports split screen, offline multiplayer |
| splitscreenonline | boolean | True if the game supports split screen, online multiplayer |

---

### Network Type

Social networks related to events (e.g., Twitter, Facebook, YouTube).

**Endpoint:** `https://api.igdb.com/v4/network_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| event_networks | Array of Event Network IDs | URLs associated with the event type |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Platform

Hardware used to run games or game delivery networks.

**Endpoint:** `https://api.igdb.com/v4/platforms`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| abbreviation | String | An abbreviation of the platform name |
| alternative_name | String | An alternative name for the platform |
| category | Category Enum | **DEPRECATED!** Use `platform_type` instead |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| generation | Integer | The generation of the platform |
| name | String | The name of the platform |
| platform_family | Reference ID for Platform Family | The family of platforms this one belongs to |
| platform_logo | Reference ID for Platform Logo | The logo of the first version of this platform |
| platform_type | Reference ID for Platform Type | The type of the platform |
| slug | String | A url-safe, unique, lower-case version of the name |
| summary | String | The summary of the first version of this platform |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |
| versions | Array of Platform Version IDs | Associated versions of this platform |
| websites | Array of Platform Website IDs | The main website |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `platform_type` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| console | 1 |
| arcade | 2 |
| platform | 3 |
| operating_system | 4 |
| portable_console | 5 |
| computer | 6 |

---

### Platform Family

A collection of closely related platforms.

**Endpoint:** `https://api.igdb.com/v4/platform_families`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| name | String | The name of the platform family |
| slug | String | A url-safe, unique, lower-case version of the name |

---

### Platform Logo

**Endpoint:** `https://api.igdb.com/v4/platform_logos`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| checksum | uuid | Hash of the object |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Platform Type

**Endpoint:** `https://api.igdb.com/v4/platform_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Platform Version

**Endpoint:** `https://api.igdb.com/v4/platform_versions`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| companies | Array of Platform Version Company IDs | Who developed this platform version |
| connectivity | String | The network capabilities |
| cpu | String | The integrated control processing unit |
| graphics | String | The graphics chipset |
| main_manufacturer | Reference ID for Platform Version Company | Who manufactured this version of the platform |
| media | String | The type of media this version accepted |
| memory | String | How much memory there is |
| name | String | The name of the platform version |
| os | String | The operating system installed on the platform version |
| output | String | The output video rate |
| platform_logo | Reference ID for Platform Logo | The logo of this platform version |
| platform_version_release_dates | Array of Platform Version Release Date IDs | When this platform was released |
| resolutions | String | The maximum resolution |
| slug | String | A url-safe, unique, lower-case version of the name |
| sound | String | The sound chipset |
| storage | String | How much storage there is |
| summary | String | A short summary |
| url | String | The website address (URL) of the item |

---

### Platform Version Company

Platform developers.

**Endpoint:** `https://api.igdb.com/v4/platform_version_companies`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| comment | String | Any notable comments about the developer |
| company | Reference ID for Company | The company responsible for developing this platform version |
| developer | boolean | |
| manufacturer | boolean | |

---

### Platform Version Release Date

**Endpoint:** `https://api.igdb.com/v4/platform_version_release_dates`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** Use `date_format` instead |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| date | Unix Time Stamp | The release date |
| date_format | Reference ID for Date Format | The format of the date |
| human | String | A human-readable representation of the date |
| m | Integer | The month (if applicable) |
| platform_version | Reference ID for Platform Version | The platform version |
| region | Reference ID for Region | The region |
| release_region | Reference ID for Release Region | **DEPRECATED!** Use `region` instead |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| y | Integer | The year |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `date_format` instead
> - `region`: DEPRECATED! Use `release_region` instead

---

### Platform Website

**Endpoint:** `https://api.igdb.com/v4/platform_websites`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** Use `type` instead |
| checksum | uuid | Hash of the object |
| trusted | boolean | |
| type | Reference ID for Website Type | The website type associated with the website |
| url | String | The website address (URL) of the item |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `type` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| official | 1 |
| wikia | 2 |
| wikipedia | 3 |
| facebook | 4 |
| twitter | 5 |
| twitch | 6 |
| instagram | 8 |
| youtube | 9 |
| iphone | 10 |
| ipad | 11 |
| android | 12 |
| steam | 13 |
| reddit | 14 |
| discord | 15 |
| google_plus | 16 |
| tumblr | 17 |
| linkedin | 18 |
| pinterest | 19 |
| soundcloud | 20 |

---

### Player Perspective

Player perspectives describe the view/perspective of the player in a video game.

**Endpoint:** `https://api.igdb.com/v4/player_perspectives`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Popularity Primitive

Popularity primitives with their source and popularity type.

**Endpoint:** `https://api.igdb.com/v4/popularity_primitives`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| calculated_at | datetime | |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| external_popularity_source | Reference ID for External Game Source | |
| game_id | Integer | |
| popularity_source | Popularity Source Enum | **DEPRECATED!** Use `external_popularity_source` instead |
| popularity_type | Reference ID for Popularity Type | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| value | bigdecimal | |

> **Deprecated Fields:**
> - `popularity_source`: DEPRECATED! Use `external_popularity_source` instead

#### Enums

**Popularity Source Enum**

| Name | Value |
|------|-------|
| igdb | 121 |

---

### Popularity Type

**Endpoint:** `https://api.igdb.com/v4/popularity_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| external_popularity_source | Reference ID for External Game Source | |
| name | String | |
| popularity_source | Popularity Source Enum | **DEPRECATED!** Use `external_popularity_source` instead |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

> **Deprecated Fields:**
> - `popularity_source`: DEPRECATED! Use `external_popularity_source` instead

#### Enums

**Popularity Source Enum**

| Name | Value |
|------|-------|
| steam | 1 |
| igdb | 121 |

---

### Region

Regions for game localization.

**Endpoint:** `https://api.igdb.com/v4/regions`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | String | This can be either 'locale' or 'continent' |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| identifier | String | The identifier of each region |
| name | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Release Date

Game release dates with platform and region details.

**Endpoint:** `https://api.igdb.com/v4/release_dates`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** Use `date_format` instead |
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| date | datetime | The date of the release |
| date_format | Reference ID for Date Format | The format of the change date |
| game | Reference ID for Game | |
| human | String | A human readable representation of the date |
| m | Integer | The month as an integer starting at 1 (January) |
| platform | Reference ID for Platform | The platform of the release |
| region | Region Enum | **DEPRECATED!** Use `release_region` instead |
| release_region | Reference ID for Release Date Region | The region of the release |
| status | Reference ID for Release Date Status | The status of the release |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| y | Integer | The year in full (e.g., 2018) |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `date_format` instead
> - `region`: DEPRECATED! Use `release_region` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| YYYYMMMMDD | 0 |
| YYYYMMMM | 1 |
| YYYY | 2 |
| YYYYQ1 | 3 |
| YYYYQ2 | 4 |
| YYYYQ3 | 5 |
| YYYYQ4 | 6 |
| TBD | 7 |

**Region Enum**

| Name | Value |
|------|-------|
| europe | 1 |
| north_america | 2 |
| australia | 3 |
| new_zealand | 4 |
| japan | 5 |
| china | 6 |
| asia | 7 |
| worldwide | 8 |
| korea | 9 |
| brazil | 10 |

---

### Release Date Region

**Endpoint:** `https://api.igdb.com/v4/release_date_regions`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| region | String | |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Release Date Status

Release date status definitions.

**Endpoint:** `https://api.igdb.com/v4/release_date_statuses`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| description | String | The description of the release date status |
| name | String | The name of the release date status |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

### Screenshot

Game screenshots.

**Endpoint:** `https://api.igdb.com/v4/screenshots`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alpha_channel | boolean | |
| animated | boolean | |
| checksum | uuid | Hash of the object |
| game | Reference ID for Game | The game this screenshot is associated with |
| height | Integer | The height of the image in pixels |
| image_id | String | The ID of the image used to construct an IGDB image link |
| url | String | The website address (URL) of the item |
| width | Integer | The width of the image in pixels |

---

### Search

Global search across multiple entity types.

**Endpoint:** `https://api.igdb.com/v4/search`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| alternative_name | String | |
| character | Reference ID for Character | |
| checksum | uuid | Hash of the object |
| collection | Reference ID for Collection | |
| company | Reference ID for Company | |
| description | String | |
| game | Reference ID for Game | |
| name | String | |
| platform | Reference ID for Platform | |
| published_at | Unix Time Stamp | The date this item was initially published by the third party |
| test_dummy | Reference ID for Test Dummy | |
| theme | Reference ID for Theme | |

---

### Theme

Video game themes.

**Endpoint:** `https://api.igdb.com/v4/themes`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| name | String | |
| slug | String | A url-safe, unique, lower-case version of the name |
| updated_at | datetime | The last date this entry was updated in the IGDB database |
| url | String | The website address (URL) of the item |

---

### Website

Website URLs, usually associated with games.

**Endpoint:** `https://api.igdb.com/v4/websites`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| category | Category Enum | **DEPRECATED!** Use `type` instead |
| checksum | uuid | Hash of the object |
| game | Reference ID for Game | The game this website is associated with |
| trusted | boolean | |
| type | Reference ID for Website Type | The website type associated with the website |
| url | String | The website address (URL) of the item |

> **Deprecated Fields:**
> - `category`: DEPRECATED! Use `type` instead

#### Enums

**Category Enum**

| Name | Value |
|------|-------|
| official | 1 |
| wikia | 2 |
| wikipedia | 3 |
| facebook | 4 |
| twitter | 5 |
| twitch | 6 |
| instagram | 8 |
| youtube | 9 |
| iphone | 10 |
| ipad | 11 |
| android | 12 |
| steam | 13 |
| reddit | 14 |
| itch | 15 |
| epicgames | 16 |
| gog | 17 |
| discord | 18 |
| bluesky | 19 |

---

### Website Type

**Endpoint:** `https://api.igdb.com/v4/website_types`

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| checksum | uuid | Hash of the object |
| created_at | datetime | Date this was initially added to the IGDB database |
| type | String | The website type |
| updated_at | datetime | The last date this entry was updated in the IGDB database |

---

## IGDB PopScore

**Introducing IGDB PopScore** - Your key to tracking the latest trends in the video game market.

Accessible through our API, IGDB PopScore offers "popularity primitives" from sources like IGDB page visits and list additions, with more sources and primitives coming in the future.

With IGDB PopScore, you can define and create your own trend and popularity indicators using individual primitives or by combining them to fit your needs. Updated every 24 hours, our data ensures you always have the latest insights into the gaming market covering all platforms.

### Currently Available PopScore Primitives

- **IGDB Visits**: Game page visits on IGDB.com
- **IGDB Want to Play**: Additions to IGDB.com users' "Want to Play" lists
- **IGDB Playing**: Additions to IGDB.com users' "Playing" lists
- **IGDB Played**: Additions to IGDB.com users' "Played" lists
- **Steam 24hr Peak Players**: Peak CCU over the past 24 hours
- **Steam Positive Reviews**: Total number of positive reviews
- **Steam Negative Reviews**: Total number of negative reviews
- **Steam Total Reviews**: Total number of reviews (positive and negative)

We’re constantly refining and expanding IGDB PopScore to ensure you have access to the most up-to-date and relevant data as possible. Stay tuned for exciting new features and data points as we continue to push the boundaries of what’s possible in the realm of video game trend analysis.

You can check the current popularity types we support by querying the API at `/popularity-types`. More details can be found under Popularity Types.

### How to use Popularity API

Start by discovering the available popularity types mentioned above:

```bash
curl 'https://api.igdb.com/v4/popularity_types' \
-d 'fields name,popularity_source,updated_at; sort id asc;' \
-H 'Client-ID: Client ID' \
-H 'Authorization: Bearer access_token' \
-H 'Accept: application/json'
```

**Result:**

```json
[
	{
		"id": 1,
		"popularity_source": 121,
		"name": "Visits"
	},
	{
		"id": 2,
		"popularity_source": 121,
		"name": "Want to Play"
	},
	{
		"id": 3,
		"popularity_source": 121,
		"name": "Playing"
	},
	{
		"id": 4,
		"popularity_source": 121,
		"name": "Played"
	},
	{
		"id": 5,
		"popularity_source": 1,
		"name": "24hr Peak Players"
	},
	{
		"id": 6,
		"popularity_source": 1,
		"name": "Postitive Reviews"
	},
	{
		"id": 7,
		"popularity_source": 1,
		"name": "Negative Reviews"
	},
	{
		"id": 8,
		"popularity_source": 1,
		"name": "Total Reviews"
	}
]
```

#### Example Use Cases

**Use case 1: Fetch top 10 games based on IGDB visits**

As an API user I'd like to fetch the top 10 games based on IGDB visits.

**Query:**

```bash
curl 'https://api.igdb.com/v4/popularity_primitives' \
-d 'fields game_id,value,popularity_type; sort value desc; limit 10; where popularity_type = 1;' \
-H 'Client-ID: Client ID' \
-H 'Authorization: Bearer access_token' \
-H 'Accept: application/json'
```

**Result:**

```json
[
  {
    "id": 15456,
    "game_id": 121,
    "popularity_type": 1,
    "value": 0.006605335786569
  },
  {
    "id": 16211,
    "game_id": 1244,
    "popularity_type": 1,
    "value": 0.005482980680773
  },
  ...
  {
    "id": 33353,
    "game_id": 135400,
    "popularity_type": 1,
    "value": 0.002741490340386
  },
  {
    "id": 17317,
    "game_id": 3277,
    "popularity_type": 1,
    "value": 0.002695492180313
  }
]
```

In the result above, you can see that the top game is the game with IGDB ID 121: [Minecraft](https://www.igdb.com/games/minecraft)

---

**Use case 2: Define custom trend metrics**

Define your own trend metrics. For example, by combining two or more primitives with equal or different weight ratios, you can create a unique popularity metric and ensure it fits your needs.

In this use case, we want to combine "Want to play" with a weight of 0.6 and "Playing" with a weight of 0.4.

For each game, calculate:
```
0.6 * ("Want to play" value) + 0.4 * ("Playing" value) = custom_popularity_value
```

To implement this, pull the values for each popularity type into your own system and combine them accordingly.

You'll need a local data structure similar to the popularity primitive with the following attributes:
- `game_id`
- `popularity_type` (Want to Play = 2, Playing = 3)
- `value`

An example SQL query that would give you the top 10 of your custom popularity:

```sql
SELECT igdb_game_id,
       SUM(CASE WHEN popularity_type_id = '2' THEN value ELSE 0 END) AS value1,
       SUM(CASE WHEN popularity_type_id = '3' THEN value ELSE 0 END) AS value2,
       (
           0.6 * SUM(CASE WHEN popularity_type_id = '2' THEN value ELSE 0 END) +
           0.4 * SUM(CASE WHEN popularity_type_id = '3' THEN value ELSE 0 END)
       ) AS weighted_score
FROM popularity_primitives
GROUP BY igdb_game_id
ORDER BY weighted_score DESC
LIMIT 10;
```

You can find detailed API documentation under [Popularity Types](#popularity-type) and [Popularity Primitives](#popularity-primitive).

---

## Webhooks

### What are Webhooks?

Webhooks allow us to push data to you when it is added, updated, or deleted. Instead of polling the API for changes, you can listen on your own HTTP endpoint (Webhook) and we will deliver the data to you.

Using Webhooks will ensure that your data is always up to date!

### How to Register Your Webhook

To register a new webhook, send a POST request to `ENDPOINT/webhooks`. The endpoint is required as it specifies what type of data you want from your webhook.

**Endpoint:** `POST https://api.igdb.com/v4/ENDPOINT/webhooks/`

The POST request should contain an `x-www-form-urlencoded` body with three parameters:

- **url**: Your prepared URL that is ready to accept data from us
- **method**: The type of data you are expecting to your URL. There are three types:
  - `create`: Sends new items from the API
  - `delete`: Sends deleted items from the API
  - `update`: Sends updated items from the API
- **secret**: Your "secret" password for your webhook. Every request from the webhook service will have your secret in the header called `X-Secret`

**Example Response:**

```json
{
    "id": "WEBHOOK_ID",
    "url": "YOUR_WEBHOOK_URL",
    "category": 1,
    "sub_category": 0,
    "active": true,
    "api_key": "YOUR_CLIENT_ID",
    "secret": "YOUR_SECRET",
    "created_at": "2018-11-25T23:00:00.000Z",
    "updated_at": "2018-11-25T23:00:00.000Z"
}
```

Once your webhook is registered, you will receive a response with the new webhook object.

### Webhook Behavior

The data will now be sent to your webhook in the body of a POST request. The data is a single JSON object representing an unexpanded entity.

> **Note:** Webhooks from DELETE do not send the entire object, only the ID.

> **Tip:** Always validate your received data with your secret!

Webhooks have an `active` field. The service will keep the webhook active as long as the webhook URL is capable of receiving data from the service. If the URL fails 5 times, the webhook will be set to inactive (`active: false`) and the service will stop sending data to this webhook.

Reactivating the webhook is done by re-registering it, which will update the active status to `true`.

> **Tip:** Re-register your webhook on service start to make sure it's always active!

### Viewing Your Webhooks

**Get all registered webhooks:**

`GET https://api.igdb.com/v4/webhooks/`

To get ALL of your registered webhooks, simply send a GET request to `/webhooks` (without the endpoint). This will return a JSON array of your webhooks.

**Get a specific webhook:**

`GET https://api.igdb.com/v4/webhooks/WEBHOOK_ID`

To get information about a specific webhook, make a GET request with the webhook ID to `/webhooks/WEBHOOK_ID` (without the endpoint).

### Removing a Webhook

**Endpoint:** `DELETE https://api.igdb.com/v4/webhooks/WEBHOOK_ID`

To remove your existing webhook, send a DELETE request to `/webhooks/WEBHOOK_ID` (without the endpoint). The Webhook ID is returned during the registration process or can be found with a GET request to `/webhooks/`.

The DELETE request will receive the deleted webhook as confirmation:

```json
{
  "id": "1234"
}
```

### Testing Webhooks

To make sure you have everything set up correctly, we have a test endpoint for the webhook service. This endpoint will send an object of your choosing to your newly created webhook.

**Endpoint:** `POST https://api.igdb.com/v4/ENDPOINT/webhooks/test/WEBHOOK_ID?entityId=ENTITY_ID`

The `entityId` is the ID of the object from the endpoint you wish to test with.

**Example:**

`POST https://api.igdb.com/v4/games/webhooks/test/42?entityId=1337`

This request will send the game object with ID 1337 to your webhook URL.

### Handling Webhooks on Your End

When receiving the webhook message on your end, you must return a `200 OK` response within 15 seconds. If the endpoint takes longer than 15 seconds to respond, the event will be deemed a failed event. Fail 5 times and the webhook will be set to inactive.

---

## CORS Proxy

### CORS

If you intend to use our API from your website you will encounter an issue with security; namely CORS Cross-Origin Resource Sharing.

There are security mechanisms in place by all major browsers to stop websites from accessing other domains without getting explicit permission. This is done through HTTP headers. So, for example, amazinggameswebsite.com cannot access api.igdb.com without us explicitly stating in the HTTP headers (Access-Control-Allow-Origin) that they have permission.

We do not offer the configuration of these headers as a service, so any browser-based JavaScript and mobile JavaScript frameworks will not be able to communicate directly with the IGDB API.

### Workaround

See the guide below for setting up a proxy, or set up a proxy using [CORS Anywhere](https://github.com/Rob--W/cors-anywhere).

### Proxy

There are a number of reasons why you may wish to proxy requests to the IGDB API:

- To have a backend that keeps track of your OAuth Application Tokens
- Caching requests to the API for better performance
- Enable application logging to track/debug usage
- Enable CORS between the proxy and applications

### How do I set up a proxy?

Proxies can be complex, but to get you started we have a simple guide to get you up and running quickly through AWS.

We have provided a simple deployment link that will let you deploy an AWS API Gateway in your own AWS account that will serve as a proxy. This Stack will also handle your Access Token rotations automatically for you.

### What will it cost?

AWS has a very generous free-tier for new users and the services used in the provided solution (API Gateway, Secrets Manager, Lambda). Please use the [AWS Pricing Calculator](https://calculator.aws/) to gauge how much this will cost you before setting up your Stack.

### Stack Setup

**Prerequisites:** You need to have an AWS account with permissions to deploy CloudFormation stacks.

**Setup Steps:**

1. Click the deployment link to get started
2. Go over the Stack Details:
   - You have to agree to the terms and conditions
   - You have to fill in your Twitch Application Credentials
   - It's recommended to protect your proxy by enabling API Keys
   - **NOTE:** Enabling Caching will come with extra costs as this is NOT covered by the Free-tier
   - **NOTE:** Enabling CORS will 'break' Protobuf responses; some libraries might not work
3. Click **Next**
4. Configure Stack Options - Nothing is required here, you can click **Next**
5. Verify Settings, click the checkbox at the bottom, then click **Create Stack**
6. You will now see the "Stack Details" screen. Hit the refresh arrow button on the right until your stack name on the left says "UPDATE_COMPLETE"
7. Click on the "Outputs" tab to get the URL to your new proxy
   - The "Resources" tab summarizes all the services deployed on your account
   - The "Template" tab displays the template used for deployment
8. You can now post requests to your URL and it will proxy to our API
   - If you enabled API Keys, you will need to specify the header `x-api-key`. The key can be found via a link through the "Resources" tab for "ApiDefaultKey"

> **Important Note:** The URL generated will end in `production`, so you will want to post to:
> `https://<your-api-gateway-unique-id>.execute-api.us-west-2.amazonaws.com/production/v4/games`

### What's next?

You can do a lot of things via API Gateway:

- Improve the security of your proxy by creating another sort of Authentication to prevent others from using up your RPS quota
- Set up your own Domain name and SSL with Route53
- Modify the path of the proxy to have it serve as the front-end to your own APIs:
  - Perform a calculation? Lambda Integration
  - Just want to store some records? DynamoDB Integration
  - Want users to be able to upload/download files? S3 Integration
- Enable request logging

### Alternatives

- **CORS:** Set up a proxy using [CORS Anywhere](https://github.com/Rob--W/cors-anywhere)

---

## Reference

### Images

> **Note:** Images that are removed or replaced from IGDB.com exist for 30 days before they are removed. Keep that in mind when designing cache logic.

#### Example

**Request:**
- **Address:** `https://api.igdb.com/v4/games/`
- **Body:**
  ```
  fields screenshots.*;
  where id = 1942;
  ```

Here we retrieve the image properties of the game with ID 1942:

```json
[{
	"id": 1942,
	"screenshots": [{
		"id": 9742,
		"game": 1942,
		"height": 1080,
		"image_id": "mnljdjtrh44x4snmierh",
		"url": "//images.igdb.com/igdb/image/upload/t_thumb/mnljdjtrh44x4snmierh.jpg",
		"width": 1920
	},
	{
		"id": 9743,
		"game": 1942,
		"height": 1080,
		"image_id": "em1y2ugcwy2myuhvb9db",
		"url": "//images.igdb.com/igdb/image/upload/t_thumb/em1y2ugcwy2myuhvb9db.jpg",
		"width": 1920
	}]
}]
```

#### Image URL Structure

**Example URL:**

```
https://images.igdb.com/igdb/image/upload/t_screenshot_med_2x/dfgkfivjrhcksyymh9vw.jpg
```

**URL Pattern:**

```
https://images.igdb.com/igdb/image/upload/t_{size}/{hash}.jpg
```

- `{size}`: One of the size types listed below
- `{hash}`: The `image_id` from the API response

The image sizes are all maximum sizes. By appending `_2x` to any size, you can get retina (DPR 2.0) sizes (e.g., `cover_small_2x`).

#### Available Image Sizes

| Name | Size | Extra |
|------|------|-------|
| cover_small | 90 x 128 | Fit |
| screenshot_med | 569 x 320 | Lfill, Center gravity |
| cover_big | 264 x 374 | Fit |
| logo_med | 284 x 160 | Fit |
| screenshot_big | 889 x 500 | Lfill, Center gravity |
| screenshot_huge | 1280 x 720 | Lfill, Center gravity |
| thumb | 90 x 90 | Thumb, Center gravity |
| micro | 35 x 35 | Thumb, Center gravity |
| 720p | 1280 x 720 | Fit, Center gravity |
| 1080p | 1920 x 1080 | Fit, Center gravity |

---

### Fields

#### What are Fields?

Fields are properties of an entity. For example, a Game field would be `genres` or `release_dates`. Some fields have properties of their own; for example, the `genres` field has the property `name`.

#### Where can Fields be used?

Fields can be used on any entity that has sub-properties, such as Games, Companies, People, etc.

#### How to use Fields

Fields are requested in a comma-separated list. For example, to get some information for some Games, Genres, Themes or anything else:

**Apicalypse:**

```
where id = (4356,189,444);
fields name,release_dates,genres.name,rating;
```

**Legacy Parameters:**

```
/games/4356,189,444?fields=name,release_dates,genres.name,rating
```

> **Note:** In Apicalypse, the `name` property of `genres` can be accessed directly with a dot (`genres.name`).

A full list of fields can be obtained by passing `*` as a field. Alternatively, you can use the meta postfix: `/games/meta` to get a list of all fields.

#### Shorthand

Another way of writing fields is to use the shorthand `f`, which achieves the same result:

```
f name,release_dates,genres.name,rating;
w id = (4356,189,444);
```

---

### Exclude

#### What is Exclude?

Exclude is a complement to the regular fields which allows you to request all fields with the exception of any number of fields specified with `exclude`.

#### How to use Exclude

Fields to be excluded are specified as a comma-separated list. For example, to get all fields except for `screenshots`:

**Apicalypse:**

```
fields *;
exclude screenshots;
```

#### Shorthand

Another way of writing exclude is to use the shorthand `x`:

```
f *;
x screenshots;
```

---

### Expander

#### What is Expander?

Some fields are actually IDs pointing to another endpoint. The expander feature is a convenient way to access these other endpoints and retrieve more information in the same query, instead of having to do multiple queries.

#### Where can Expander be used?

Expands are specified among the regular fields in the body of the query.

#### How to use Expander

Fields can be expanded with a dot followed by the fields you want to access from a certain endpoint.

#### Examples

**Example 1: Without Expander**

In this example, we request the fields `name` and `genres` for the game The Witcher 3 (ID 1942):

```
fields name,genres;
where id = 1942;
```

This query will only return IDs for the genres:

```json
[
    {
        "id": 1942,
        "genres": [12, 31],
        "name": "The Witcher 3: Wild Hunt"
    }
]
```

**Example 2: With Expander**

For some use cases, the ID is all that is needed, but often more data is required. This is when the expander feature comes in handy:

```
fields name,genres.name;
where id = 1942;
```

This example with expander retrieves the name of each genre:

```json
[
    {
        "id": 1942,
        "genres": [
            {
                "id": 12,
                "name": "Role-playing (RPG)"
            },
            {
                "id": 31,
                "name": "Adventure"
            }
        ],
        "name": "The Witcher 3: Wild Hunt"
    }
]
```

**Example 3: Using Wildcard**

You can use a wildcard character `*` to retrieve all data from genres:

```
fields name,genres.*;
where id = 1942;
```

This returns all available data for each genre:

```json
[
    {
        "id": 1942,
        "genres": [
            {
                "id": 12,
                "created_at": 1297555200,
                "name": "Role-playing (RPG)",
                "slug": "role-playing-rpg",
                "updated_at": 1323216000,
                "url": "https://www.igdb.com/genres/role-playing-rpg"
            },
            {
                "id": 31,
                "created_at": 1323561600,
                "name": "Adventure",
                "slug": "adventure",
                "updated_at": 1323561600,
                "url": "https://www.igdb.com/genres/adventure"
            }
        ],
        "name": "The Witcher 3: Wild Hunt"
    }
]
```

---

### Filters

#### What are Filters?

Filters are used to sift through results to get what you want. You can exclude and include results based on their properties. For example, you could remove all Games where the rating was below 80 (`where rating >= 80`).

#### How to use Filters

Filters can be added using the `where` clause:

**Example:**

- **Address:** `https://api.igdb.com/v4/games/`
- **Body:**
  ```
  search "zelda";
  where rating >= 80 & release_dates.date > 631152000;
  ```

#### Where can Filters be used?

Filters can be used on any entity that has sub-properties, such as Games, Companies, People, etc.

#### Available Filter Operators

| Operator | Description |
|----------|-------------|
| `=` | Equal: Exact match |
| `!=` | Not Equal: Exact match |
| `>` | Greater than (works only on numbers) |
| `>=` | Greater than or equal to (works only on numbers) |
| `<` | Less than (works only on numbers) |
| `<=` | Less than or equal to (works only on numbers) |
| `= "String"*` | **Prefix:** Exact match on the beginning of the string, can end with anything (case sensitive) |
| `~ "String"*` | **Prefix:** Exact match on the beginning of the string, can end with anything (case insensitive) |
| `= *"String"` | **Postfix:** Exact match at the end of the string, can start with anything (case sensitive) |
| `~ *"String"` | **Postfix:** Exact match at the end of the string, can start with anything (case insensitive) |
| `= *"String"*` | **Infix:** Exact match in the middle of the string, can start and end with anything (case sensitive) |
| `~ *"String"*` | **Infix:** Exact match in the middle of the string, can start and end with anything (case insensitive) |
| `!= null` | The value is not null |
| `= null` | The value is null |
| `[V1,V2,...Vn]` | The value exists within the (comma separated) array (**AND** between values) |
| `![V1,V2,...Vn]` | The values must not exist within the (comma separated) array (**AND** between values) |
| `(V1,V2,...Vn)` | The value has any within the (comma separated) array (**OR** between values) |
| `!(V1,V2,...Vn)` | The values must not exist within the (comma separated) array (**OR** between values) |
| `{V1,V2,...Vn}` | Exact match on arrays (does not work on IDs, strings, etc) |

#### Filter Examples

**Filter by multiple platforms:**

To get games released on **PS4 OR XBOX ONE OR PC:**

```
fields name;
where release_dates.platform = (48,49,6);
```

To get games released on **PS4 AND XBOX ONE AND PC:**

```
fields name;
where release_dates.platform = [48,49,6];
```

To get games released **only on PC:**

```
fields name;
where release_dates.platform = 6;
```

To get games released for **PC OR any other platform:**

```
fields name;
where release_dates.platform = (6);
```

**Combining Multiple Filters:**

It is possible to use logical operators between filters:

```
fields name,platforms,genres.name;
where (platforms = [6,48] & genres = 13) | (platforms = [130,48] & genres = 12);
```

The response from this example query will be games that fulfill one or both of two sets of requirements:

- Games released for both PC (6) and PS4 (48) and also has the genre Simulator (13)
- Games released for both Switch (130) and PS4 (48) and also has the genre Role-Playing (12)

**Prefix, Postfix and Infix Matching:**

**Prefix** - Filtering for game names beginning with "Super":

```
fields name;
where name = "Super"*;
```

This will return games such as Super Mario World.

**Postfix** - Filtering for game names ending with "World":

```
fields name;
where name = *"World";
```

This will also return games such as Super Mario World.

**Infix** - Filtering for game names containing "Smash" anywhere:

```
fields name;
where name = *"Smash"*;
```

This will return games such as Super Smash Bros.

**Case Insensitive** - Using `~` instead of `=`:

```
fields name;
where name ~ *"Smash"*;
```

**Removing Erotic Games:**

Some queries may return games with erotic themes. All erotic games in the database have the theme 'erotic' (ID = 42). You can remove them from your responses with this filter:

```
fields name;
where themes != (42);
```

---

### Sorting

#### What is Sorting?

Sorting is used to order results by a specific field.

#### How to use Sorting

You can order results like this:

```
sort release_dates.date desc;
where rating >= 80;
```

You can use `desc` (descending) or `asc` (ascending) for the sort order.

**Example: Order by rating**

```
fields name,rating;
sort rating desc;
where rating != null;
```

#### Where can Sorting be used?

Ordering can be used on any entity.

---

### Search

#### What is Search?

Search based on name. Results are sorted by similarity to the given search string.

#### Searchable Endpoints

- Characters
- Collections
- Games
- People
- Platforms
- Themes

#### How to use Search

Specify which endpoint to search in the request URL. The search string is entered in the body using the `search` keyword:

**Example:**

```
search "zelda";
```

---

### Pagination

#### Using Limit

The default limit is 10. The maximum value you can set for `limit` is 500.

**Example:**

```
limit 33;
```

#### Using Offset

Offset starts the list at a specific position. This example will start at position 22 and give 33 results:

```
limit 33;
offset 22;
```

---

### Protocol Buffers

Google Protocol Buffers is a language-neutral method for serializing structured data. The IGDB API supports responses in this format, so you do not have to write your own serialization libraries. Since this is language-neutral, it is supported by a variety of languages.

#### How to use Protocol Buffers

1. Generate the objects in your language of choice with [IGDB's Protobuf file](https://api-docs.igdb.com/images/igdb.proto)
2. This file contains the mapping of the entire IGDB API and can be used to generate wrappers, code, and tooling in any programming language
3. The protobuf file is created in accordance with the proto3 specification

There are plenty of examples on how to do this online and on the [Protobuf Site](https://developers.google.com/protocol-buffers).

#### Requesting Protobuf Responses

To start receiving protobuf-compatible responses from the API, add `.pb` at the end of your request:

```
https://api.igdb.com/v4/games.pb
```

Then use your generated files to parse the response into the expected object.

---

### Tag Numbers

Tag numbers are automatically generated numbers which provide a compact and fast way to do complex filtering on the IGDB API. The number calculation can be easily achieved with any programming language.

The basis of the calculation is a 32-bit integer, where the first 4 bits contain the object type ID, and the remaining 28 bits represent the ID of the object we are generating the tag number for.

Using this method, a flat index of custom object 'hashes' can be maintained in which the search and filtering is faster than using conventional methods.

#### Object Types Using Tags

| Type ID | Name |
|---------|------|
| 0 | Theme |
| 1 | Genre |
| 2 | Keyword |
| 3 | Game |
| 4 | Player Perspective |

#### Tag Number Calculation Examples

**Example 1: JavaScript**

To find all games related to the Shooter genre:

```javascript
const genreTypeID = 1; // The type ID from the table above
const shooterGenreID = 5; // The Shooter genre's ID from the genres endpoint
let tagNumber = genreTypeID << 28; // Bit-shifting by 28 bits. Result: 268435456
tagNumber |= shooterGenreID; // Bitwise OR operation. Result: 268435461
```

**Query:**

```
where tags = (268435461);
```

**Example 2: Python**

To find all games related to the 'moba' keyword:

```python
keywordTypeID = 2  # The keyword's type ID from the table above
keywordID = 148  # The ID of the 'moba' keyword
tagNumber = keywordTypeID << 28  # Bit-shifting by 28 bits. Result: 536870912
tagNumber |= keywordID  # Bitwise OR operation. Result: 536871060
```

**Query:**

```
where tags = (536871060);
```

---

### Multi-Query

Multi-Query is a way to request a large amount of information in one request! With Multi-Query, you can request multiple endpoints at once. It also works with multiple requests to a single endpoint.

**Endpoint:** `POST https://api.igdb.com/v4/multiquery`

#### Syntax Structure

The Multi-Query syntax is made up of three pieces:
1. Endpoint name
2. Result name (given by you)
3. The Apicalypse query inside the body `{}`

> **Important:** You can only run a maximum of 10 queries.

#### Examples

**Example 1: Get count of platforms**

```
query platforms/count "Count of Platforms" {
  // here we can have additional filters
};
```

**Result:**

```json
[
  {
    "name": "Count of Platforms",
    "count": 155
  }
]
```

**Example 2: Get PlayStation 4 Exclusives**

```
query games "Playstation Games" {
	fields name,platforms.name;
	where platforms != null & platforms = {48};
	limit 1;
};
```

**Result:**

```json
[
    {
        "name": "Playstation Games",
        "result": [
            {
                "id": 52826,
                "name": "Skate 4",
                "platforms": [
                    {
                        "id": 48,
                        "name": "PlayStation 4"
                    }
                ]
            }
        ]
    }
]
```

**Example 3: Combining multiple queries**

```
query platforms/count "Count of Platforms" {
  // here we can have additional filters
};

query games "Playstation Games" {
	fields name,platforms.name;
	where platforms != null & platforms = {48};
	limit 1;
};
```

**Result:**

```json
[
    {
        "name": "Count of Platforms",
        "count": 155
    },
    {
        "name": "Playstation Games",
        "result": [
            {
                "id": 52826,
                "name": "Skate 4",
                "platforms": [
                    {
                        "id": 48,
                        "name": "PlayStation 4"
                    }
                ]
            }
        ]
    }
]
```

---

## APICalypse

### APICalypse Cheatsheet

APICalypse is the query language used for this API, which greatly simplifies how you can query your requests compared to the URL parameters used in API V2.

#### Fields

Fields are used to select which fields you want back from your request to the API.

- **Command:** `fields` (shorthand: `f`)
- **Wildcard:** Use `*` to get all fields

```
fields name,release_dates,genres.name,rating;
f name,release_dates,genres.name,rating;
```

#### Exclude

Commonly used with the wildcard `*`, this command excludes the fields you select.

- **Command:** `exclude` (shorthand: `x`)

```
fields *;
exclude tags,keywords;

f *;
x tags,keywords;
```

#### Where

Where is best described as a filter. With `where`, you can filter on specific fields.

- **Command:** `where` (shorthand: `w`)

```
fields *;
where genres = 4;

f *;
w genres = 4;
```

#### Limit

Limit describes how many results you will get back from the API. The default value is 10.

- **Command:** `limit` (shorthand: `l`)

```
fields *;
limit 50;

f *;
l 50;
```

#### Offset

Offset describes how many results you will skip over. Default is 0. Offset is often used together with Limit for pagination.

- **Command:** `offset` (shorthand: `o`)

```
limit 50;
offset 50;

l 50;
o 50;
```

#### Sort

Use Sort to order the results to your liking.

- **Command:** `sort` (shorthand: `s`)
- **Direction:** `asc` (ascending) or `desc` (descending)

```
fields *;
sort rating asc;

f *;
s rating desc;
```

#### Search

To find a specific title, you can use Search.

- **Command:** `search` (no shorthand available)

> **Tip:** Search has its own endpoint where it's useful to add filters for specific kinds of results (e.g., `where game != null;` for only games).

```
search "Halo";
fields name;

search "Halo";
f name;
```

#### Other Shortcuts

- **Null:** Can be written as `null` or `n`
- **Booleans:** Can be written as `true`/`t` or `false`/`f`

---

## Migration: Enums to Tables

### Important Changes Coming to the IGDB API

We're announcing upcoming changes to the IGDB API that will affect how certain data fields are structured and accessed. These changes are designed to make our gaming database more dynamic and better suited to the evolving gaming industry.

### Key Changes

We're moving away from using static enum values in our API to using more flexible table-based structures. While this is primarily an internal change, it affects how certain fields are named in our API. To ensure a smooth transition:

- All current enum values will remain the same in the new table structure
- Only the field names are changing, not the values they contain
  - **NOTE:** Changes are expected for the Age Rating Categories. IDs will not reflect the same enum values here.
- This change will allow us to evolve our data structure more efficiently in the future
- This change will allow you to expand these fields instead of keeping hardcoded enums

### What is Changing?

Several field names are being standardized across our endpoints for better clarity and consistency:

| Endpoint | Current Field | New Field |
|----------|---------------|-----------|
| age_rating | category | organization |
| age_rating | rating | rating_category |
| character | gender | character_gender |
| character | species | character_species |
| companies | change_date_category | change_date_format |
| companies | start_date_category | start_date_format |
| company_website | category | type |
| external_game | category | external_game_source |
| external_game | media | game_release_format |
| platform | category | platform_type |
| website | category | type |

Additionally, we're adding some new fields:

- The `age_rating` endpoint will now use `rating_content_descriptions` instead of `content_descriptions` (replacing `age_rating_content_descriptions` with `age_rating_content_descriptions_v2`)
- The `companies` endpoint will have a `status` field for active, defunct, merged, or renamed

### New Endpoints Replacing Enum Values

- `age_rating_organizations`
- `age_rating_categories`
- `age_rating_content_descriptions_v2`
- `character_genders`
- `character_species`
- `company_status`
- `company_websites`
- `date_formats`
- `external_game_sources`
- `game_release_formats`
- `game_status`
- `game_types`
- `platform_types`
- `release_date_regions`
- `website_types`

### Datadumps

All of these changes will be reflected in the daily data dumps.

### Migration Timeline

- **Migration Period:** February 18 to August 31 (6 months)
- During this period, both old and new field names will be available
- Monthly reminders will be sent to all API users about the upcoming deprecation
- After the migration period, the old field names will be removed

### How Does This Affect You?

If your application uses any of the fields listed above, you'll need to update your code to use the new field names within the next 6 months. The current field names will be removed after the migration period ends.

### Migration Recommendations

1. Begin updating your applications to use the new field names as soon as possible
2. Test your applications thoroughly with the new field names
3. Complete all necessary changes before the end of the 6-month migration period
4. Keep an eye on Discord for monthly deprecation reminders

### Questions or Concerns?

If you have any questions about these changes or need assistance with migration, please:

- Review our updated API documentation
- Reach out to our support team
- Join our Discord community for discussions

We're committed to making this transition as smooth as possible for all our API users.

---

## Partnership

Interested in using the API for a commercial project? No problem, we allow commercial usage. Get in touch with us about our partner program!

### How to Register

To register for a commercial agreement, reach out to [partner@igdb.com](mailto:partner@igdb.com)

### Exclusive Features

- Automatic data dumps every 24 hours
- More features coming soon

---

## Data Dumps

All endpoints are available as CSV Data Dumps!

Daily updated CSV Data Dumps can be used to kickstart your projects or keep your data up to date (within 24 hours).

> **Note:** Data dumps are exclusively available to our Data Partners.

### Listing Dumps

To list the available data dumps, make a GET request to `/dumps`.

**Endpoint:** `GET https://api.igdb.com/v4/dumps`

This will return a list of available Data Dumps describing the endpoint, file name, and updated at.

**Example Response:**

```json
[
    {
		"endpoint": "games",
		"file_name": "1234567890_games.csv",
		"updated_at": 1234567890
	}
]
```

### Downloading CSV

To get the download link for the CSV files, make a GET request to `/dumps/ENDPOINT`.

**Endpoint:** `GET https://api.igdb.com/v4/dumps/ENDPOINT`

The response object will contain:
- The download link for the CSV
- The schema version
- The schema JSON structure of the data

**S3 Download URL:**
The download URL is a presigned S3 URL that is valid for 5 minutes.

**Schema:**
The `schema_version` and `schema` will reflect the current data structure and data type that the dump is using. The schema version number will change when the schema changes, so if you are planning on an automated setup, you will need to keep this in mind.

**Example Response:**

```json
{
	"s3_url": "S3_DOWNLOAD_URL",
	"endpoint": "games",
	"file_name": "1234567890_games.csv",
	"size_bytes": 123456789,
	"updated_at": 1234567890,
	"schema_version": "1234567890",
	"schema": {
		"id": "LONG",
		"name": "STRING",
		"url": "STRING",
		"franchises": "LONG[]",
		"rating": "DOUBLE",
		"created_at": "TIMESTAMP",
		"checksum": "UUID"
	}
}
```

---

## FAQ

### Business-Related FAQ

**1. I want to use the API for a commercial project, is it allowed?**

Yes, we offer commercial partnerships for users looking to integrate the API in monetized products. From our side, as part of the partnership, we ask for user-facing attribution to IGDB.com from products integrating the IGDB API.

For more details on that process, please reach out to [partner@igdb.com](mailto:partner@igdb.com)

**2. What is the price of the API?**

The API is free for both non-commercial and commercial projects.

**3. Am I allowed to store/cache the data locally?**

Yes. In fact, we prefer if you store and serve the data to your end users. You remain in control over your user experience while alleviating pressure on the API itself.

**4. Regarding user-facing attribution (relating to the commercial partnership), any specific guidelines?**

Not really. We expect fair attribution, i.e., attribution that is visible to your users and located in a static location (e.g., not in a change log).

**5. What happens with the data retrieved in the case of partnership termination?**

You are allowed to keep all data you retrieve from the API, and we will not ask you to remove the data in case of partnership termination.

**6. We don't wish to attribute IGDB.com as part of the partnership. Are there any other options?**

Yes. If you have data that we think will complete the overall IGDB data set and you are willing to share that data with us, we can opt for this approach instead. Please be aware, however, that we are only interested in publicly available data that we can re-distribute using this API.

---

### Technical-Related FAQ

**1. Can I use Twitch User Credentials to access the API?**

The IGDB API uses Application Credentials to authenticate. You cannot use user credentials to authenticate API requests.

More information about authentication can be found in the [documentation](#authentication).

**2. The requested images are in the wrong format!**

Requesting images using the API returns a default image URL using the `t_thumb` format. To request larger image sizes, you should manually create your own image URL using the `image_id` and the appropriate image size.

Example: `https://images.igdb.com/igdb/image/upload/t_{size}/{image_id}.png`

More information about images and image sizes can be found in our [documentation](#images).

**3. Why am I receiving a CORS error?**

The IGDB API does not support browser requests (CORS) for security reasons. This is because the request would leak your access token! We suggest that you create a backend proxy which authenticates and queries the API directly, and can be set up as a trusted connection for your client application.

For more information, see our [documentation](#cors-proxy).

**4. My AccessToken stopped working, why?**

Your Access Token is only active for 60 days, and your application can only have 25 active Access Tokens at one time. Going over this limit starts to inactivate older tokens.

**5. Why am I only receiving IDs?**

An empty request will only yield a list of IDs. To request more information in a single request, you should expand your request.

Example: `fields *, cover.*;`

More information about [expanding requests](#expander).

**6. Why am I only receiving 10 items, how do I get more?**

The default item limit is set to 10. To edit this limit, simply specify the limit in your request.

Example: `limit 50;`

The maximum limit is set to 500 items/request.
