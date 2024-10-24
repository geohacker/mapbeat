
# OSM Changeset WebSocket Feed

This project sets up a Lambda that listens to the [real-changesets](https://registry.opendata.aws/real-changesets/) SNS and provides an API Gateway WebSocket connections for clients to receive the data. At the moment, each event is the metadata of the changeset that looks like this:

```
{
  "id": "158212207",
  "created_at": "2024-10-22T13:33:41Z",
  "closed_at": "2024-10-22T13:33:42Z",
  "open": "false",
  "user": "adster546",
  "uid": "18624923",
  "min_lat": "-31.9943481",
  "min_lon": "115.9272943",
  "max_lat": "-31.9732393",
  "max_lon": "115.9494037",
  "comments_count": "0",
  "changes_count": "17",
  "tag": [
    {
      "k": "changesets_count",
      "v": "3219"
    },
    {
      "k": "comment",
      "v": "various connectivity and crossing updates"
    },
    {
      "k": "created_by",
      "v": "iD 2.30.4"
    },
    {
      "k": "host",
      "v": "https://www.openstreetmap.org/edit"
    },
    {
      "k": "imagery_used",
      "v": "Esri World Imagery"
    },
    {
      "k": "locale",
      "v": "en-AU"
    }
  ],
  "bbox": {
    "left": "115.9272943",
    "bottom": "-31.9943481",
    "right": "115.9494037",
    "top": "-31.9732393"
  }
}
```
