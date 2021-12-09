# Galactic Survival: CLI Edition

Survive the harshness of the unknown with your crew! A small resource-management puzzle game.

## Roadmap

 - [x] Basic resource gathering
 - [x] Four endings
 - [ ] Find a way to better balance upgrades
 - [ ] Find a way to better balance storage
 - [ ] Add more challenge to maintaining your approval rating (random fluctuations? moral dilemmas?)
 - [ ] Balance in general

## Did you say "CLI Edition"?

Yes, I'd like to make a Gemini version (and eventually a standalone GUI version) of this game eventually.

## Known issues (spoilers ahead)

 - "Meh" difficulty is what most games would call "easy mode", and anything below that is child's play.
 - In contrast, "I like to eat nails" is probably impossible (I'd never know; I haven't tried it).
 - You can cheese the Scout bot system by sending bots on short missions, since less minutes being simulated == less chances for the bot to get attacked.
    - I even tried to fix this by making the bots lose a fixed 5-20 of each resource instead of the original 25-50%, but it's still easy to just spam short missions until you have more rations and water than you know what to do with.
 - Once you have ~500 days worth of 3 ration meals and water, you really don't have to worry about resources at all, since you'll get enough from your bots to avoid starvation or dehydration.
    - Maybe there could be a random event where you lose a bunch of water/rations? It shouldn't be too often but enough to keep you from sitting pretty with 18,000 3-ration days and 500,000 days worth of water.
 - Once all of your Scout bots are at A+ in every stat there really isn't a reason to spend money at all.
    - Maybe bots' programming can degrade over time, forcing you to spend coins to upgrade them back to their original selves?
 - Stats in general are misleading.
    - The only one that does what it says on the tin is Attack Avoidance, which lowers the chance that an attack will happen on any given minute. The others just affect the chance of the thing that happens that minute being "the bot found rations/water/artifacts".
    - Maybe rations/water/artifacts stats can correlate to how much of a resource you get? With a 100 being "all of the yield I was supposed to get" and a 0 being "nada"?
