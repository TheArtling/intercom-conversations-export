# Intercom Conversations Export

This is a little script that exports conversations from Intercom and saves them
as `.txt` files.

## Configuration

First, create a `settings.py` file based on the `settings.py.sample` file.

Set your `INTERCOM_TOKEN` and set the `OUTPUT_PATH` setting to an absolute path.
This is where this script will store all it's output.

## Fetching the raw data

Then run `python fetcher.py` - this script will download paginated lists where
each page contains information about 20 conversations. The script will save one
file per page into the folder `raw_data/conversation_pages`.

Next, this script will download each individual conversation and save the JSON
object for each conversation into the folder `raw_data/single_conversations`.

## Extracting the conversations

Finally, run `python extractor.py` - this script will read the previously
downloaded conversation JSON objects and save them all as text-files. Each
conversation will have the date as the filename and will be stored in a folder
that matches the user's email address (if known) or the user ID. If a
conversation contains images, these will be downloaded and put into the same
folder as the conversation file.

A conversation text file looks like this:

```txt
Conversation ID: 25272772056
Started on January 06, 2020 at 10:41 AM +08
Landed on https://theartling.com/en/art/?country=japan
---
06/01/2020 10:41 AM | Operator - admin : Hi there, Looking for something specific, or have a question about an item? Let me know and I'd be happy to help. 😊
06/01/2020 10:41 AM | User : hello
06/01/2020 10:41 AM | User : We are working on a restaurant project and interested in specifying art from you guys.
06/01/2020 10:42 AM | User : Do you have any good suggestion that you can share with us? Thank you so much!
06/01/2020 10:44 AM | Operator - bot : The Artling typically replies in a day.
09/01/2020 18:37 PM | Operator - admin : Action - assignment
```
