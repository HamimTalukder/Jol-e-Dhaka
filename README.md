# Jol Abaddho Map (Dhaka Waterlogging Alert Map)
#### Video Demo: <URL HERE>
#### Description:

Jol Abaddho Map is a web application that lets people in Dhaka report and view waterlogging in real time. Every monsoon season, many roads and neighborhoods in Dhaka become flooded after heavy rain, and there is no easy, public, crowd-sourced way to find out which areas are currently affected before leaving home. This project tries to solve that with a simple map where anyone can click a location, describe how bad the water is, and instantly share that with everyone else viewing the map.

**TODO before submitting:** replace this paragraph and the ones below with your own words. Explain, in your own voice, why you picked this idea, what was hard about it, and any choices you made differently from how it's described here. CS50 expects the README to reflect your own understanding of your project, not just a description of what the code does.

## How it works

When someone visits the site, they see a map of Dhaka with colored markers showing every waterlogging report that is still active. Yellow markers mean light (ankle-deep) water, orange means moderate (knee-deep), and red means severe (impassable). Clicking a marker opens a popup with the area name, a short description, when it was reported, and two buttons: "Still there" and "Cleared", which any logged-in user can use to keep the map accurate.

To keep the map from filling up with outdated information, every report automatically expires 24 hours after it is submitted. If someone confirms with "Still there," the report's expiry is pushed back by another 12 hours. If someone marks it "Cleared," it disappears from the map immediately. This was the main design problem I had to think through: a lot of crowd-sourced apps end up full of stale data because nothing ever gets removed. Building the expiry logic directly into the database query (`WHERE status = 'active' AND expires_at > datetime('now')`) instead of relying on a separate cleanup script felt like the simplest way to solve that with the SQL I already knew from this course.

To submit a report, a user has to register and log in first, which helps discourage spam compared to letting anyone post anonymously. On the report page, they click anywhere on a smaller map to drop a pin, choose a severity level from a dropdown, and optionally add an area name and description. The browser's Geolocation API is used to try to center that map on the user's current location automatically, though they can still click anywhere else if they want to report a different area.

## Why these tools

I used Flask and SQLite because they were the tools I learned in this course, and I wanted a stack I actually understood well enough to debug on my own. For the map itself, I used Leaflet.js with OpenStreetMap tiles instead of Google Maps, mainly because it doesn't require an API key or billing account, which made it much easier to get running quickly as a student project.

## File by file

- **app.py** contains all of the Flask routes: the homepage, the JSON API endpoint the map fetches data from, the report submission form, the confirm/clear actions, and the login/register/logout routes. Login and registration follow the same pattern taught in this course's Finance problem set, using `werkzeug.security` to hash passwords instead of storing them in plain text.
- **helpers.py** defines the `login_required` decorator used to protect the report, confirm, and clear routes so only logged-in users can use them.
- **schema.sql** defines the two database tables: `users` and `reports`. I kept this deliberately simple with only two tables instead of adding a separate table for confirmations, since a report only needs one expiry timestamp that gets pushed back, not a full history of every confirmation.
- **templates/** holds the Jinja HTML templates: `layout.html` is the shared base template with the navigation bar and flashed messages, `index.html` shows the main map, `report.html` is the submission form, and `login.html`/`register.html` handle authentication.
- **static/styles.css** contains all of the site's styling. I kept the design intentionally simple and uncluttered — a single blue accent color, no frameworks, and a layout that collapses cleanly on small screens, since most people would realistically check this on their phone before leaving the house.
- **static/script.js** runs on the homepage. It initializes the Leaflet map, fetches the current reports from `/api/reports`, and draws a colored marker with a popup for each one.
- **static/report.js** runs on the report page. It initializes a second, smaller map, listens for clicks to place a pin and fill in the hidden latitude/longitude fields, and tries to auto-center the map using the browser's location.

## Design choices I debated

TODO: Add a paragraph here about any decisions you went back and forth on — for example, whether to require login just to view the map (I decided not to, so it stays useful to anyone, even without an account), whether to support photo uploads (left out for now to keep the scope manageable), or anything else you changed your mind about while building it.

## Limitations and possible future work

Right now the app doesn't support photo uploads, doesn't have any way to remove clearly fake reports, and doesn't send notifications. A logical next step would be adding a simple admin view to moderate obviously spam reports, and possibly a historical view showing which areas flood most often over time.

## Acknowledgment of AI tool use

Parts of this project's code structure (the Flask route patterns, the Leaflet.js setup, and this README template) were written with help from Claude, an AI assistant made by Anthropic, as permitted by CS50's final project policy on using AI tools as helpers. I reviewed, tested, and understand the code in this submission.
