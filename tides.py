# import necessary libraries for data retrieval and drawing to Inky pHAT
import urllib.request, json, datetime, time
from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
from font_fredoka_one import FredokaOne

# define Inky pHAT parameters
# change "red" in line below as appropriate for your display
inky_display = InkyPHAT("red")
inky_display.set_border(inky_display.BLACK)
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)
width = inky_display.WIDTH
percentwidth = 100 / width

# draw down data from the UK Hydrographic Office
# replace <id> with your station id
# replace <key> with your subscription key
with urllib.request.urlopen("https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations/<id>/TidalEvents?duration=2&key=<key>") as url:
    data = json.load(url)
    datalength = len(data)
    # cycle through data to find next event
    for x in data:
        event = (x['EventType'])
        at = (x['DateTime'])
        at = at[:19]
        when = datetime.datetime.strptime(at,"%Y-%m-%dT%H:%M:%S")
        unix = datetime.datetime.timestamp(when)
        now = time.time()
        if unix > now:
            break
        previous_event = event
        previous_at = unix

# calculate minutes until next event
next = (unix - now) / 60

# calculate minutes since previous event
previous = (now - previous_at) / 60

# calculate time between events
total = next + previous

# calculate what percentage is represented by a single minute
percent = 100 / total

# multiply percentage by time since last event to find elapsed percentage
progress = percent * previous

if event == "LowWater":
    progress = 100 - progress

# calculate start point and set multiplier
if progress < 8.33:
    start = 0
    multiplier = 1
elif progress > 8.33 and progress < 25:
    start = 8.33
    multiplier = 2
elif progress > 25 and progress < 50:
    start = 25
    multiplier = 3
elif progress > 50 and progress < 75:
    start = 50
    multiplier = 3
elif progress > 75 and progress < 91.66:
    start = 75
    multiplier = 2
else:
    start = 91.66
    multiplier = 1

#subtract completed start point from minutes remaining to find remainder
remainder = progress - start

#calculate percent value of remaining minutes
remainder_percent = percent * remainder

#multiply remaining minutes by multiplier
remainder_percent = remainder_percent * multiplier

calculated = remainder_percent + start
bar = calculated
barout = (width / 100) * calculated

event_time = at[11:16]

if event == "LowWater":
    e = "Low tide at " + event_time
else:
    e = "High tide at " + event_time

mid = inky_display.HEIGHT / 2
font = ImageFont.truetype(FredokaOne, 20)
low = "Low"
high = "High"
w, h = font.getsize(high)
w1, h1 = font.getsize(e)

draw.line(((0,inky_display.HEIGHT * .33), (inky_display.WIDTH, inky_display.HEIGHT * .33)), fill = 1, width = 1)
draw.line(((0,inky_display.HEIGHT * .66), (inky_display.WIDTH, inky_display.HEIGHT * .66)), fill = 1, width = 1)
draw.rectangle(((0,inky_display.HEIGHT * .33), (barout,inky_display.HEIGHT * .66)), fill = 2, width = 1)
draw.text((5,0), low, inky_display.BLACK, font)
draw.text((width - 5 - w, 0), high, inky_display.BLACK, font)
draw.text(((width - w1) / 2, inky_display.HEIGHT - h1), e, inky_display.BLACK, font)
inky_display.set_image(img)
inky_display.show()
