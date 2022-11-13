from save import Save
import json, textwrap, traceback, sys, time, os
from stardate import MAX_STARDATE

eightycol = lambda s: print(textwrap.fill(s,80))

save = None
new_save = False
try:
	with open("save.json") as f:
		save = Save.from_dict(json.load(f))
except FileNotFoundError: pass
except:
	traceback.print_exc()
	sys.exit(0)
if save == None:
	save = Save()
	save.initialize()
	new_save = True

def header():
	global save
	print(r"  ____       _            _   _        ____                   _            _")
	print(r" / ___| __ _| | __ _  ___| |_(_) ___  / ___| _   _ _ ____   _(_)_   ____ _| |")
	print(r"| |  _ / _` | |/ _` |/ __| __| |/ __| \___ \| | | | '__\ \ / / \ \ / / _` | |")
	print(r"| |_| | (_| | | (_| | (__| |_| | (__   ___) | |_| | |   \ V /| |\ V / (_| | |")
	print(r" \____|\__,_|_|\__,_|\___|\__|_|\___| |____/ \__,_|_|    \_/ |_| \_/ \__,_|_|")
	print("")
	print("-"*80)
	print("")

def intro():
	eightycol(f"On stardate {save.camp.date}, you and {save.camp.survivors} other survivors were trapped on {save.camp.name}, a small planet in the middle of galactic nowhere. Your only connection to the outside galaxy is through your mission's original sponsor, ACME Corp, who lacks the funds to send a ship to retrieve you.")
	print("")
	eightycol("After some arguing, it was decided that you, the mission's original captain, would be put in charge of keeping everyone alive and well.")
	print("")
	print(f"Unfortunately, you and your crew are not alone on {save.camp.name}.")
	print("")
	eightycol("Specifically, large, hostile beasts roam the surface, making it far too dangerous to go foraging for resources. Luckily, ACME Corp had foreseen this, and equipped your mission with 3 Scout-class retrieval bots. However, to call these bots basic would be an insult to basic things. They'll need upgrades.")
	print("")
	eightycol("Each upgrade costs 50 coins. (Luckily, ACME *does* have the resources to pay for any artifacts the Scouts might find, so you do have a source of income.) However, each upgrade can only be given to one bot. Choose wisely.")
	print("")
	eightycol("Well, it's in your hands, Captain. Best of luck to you and your crew.")
	print("")

def game_over(good_ending=False):
	global save
	text = "GAME OVER"
	if good_ending:
		text = "THE END"
	text = " ".join(text)
	print("-"*80)
	print(f"{text:^80s}")
	print("-"*80)
	save.game_over = True

def starve_ending():
	global save
	save.days_without_food += 1
	eightycol("You and your crew look at each other. There's not enough rations to go around.")
	print()
	if save.days_without_food<15:
		eightycol('You\'re the first to speak up. "I won\'t take any today."')
		print()
		eightycol('Then your first mate. "Neither will I."')
		print()
		eightycol('One by one, each of the survivors announces they won\'t be eating today.')
		print()
		eightycol('You sit in solidarity, daring the forces of nature to act.')
		print()
	else:
		eightycol('You all are emaciated from days of not eating.')
		print()
		eightycol('You all look at each other.')
		print()
		eightycol('Everything around you fades to black...')
		print()
		eightycol('You have starved.')
		print()
		game_over()
		return True

def dehydrate_ending():
	global save
	save.days_without_water+=1
	if save.days_without_water==1:
		eightycol("The camp has run out of water. Nothing seems to be going bad yet, but if you don't get water soon, bad things will happen.")
		print()
	elif save.days_without_water==2:
		eightycol("Everybody is complaining of headaches. You hope the scouts will arrive with water soon.")
		print()
	elif save.days_without_water==3:
		eightycol("People are starting to see things that aren't there. If the scouts don't arrive with water tomorrow, you'll all be done for.")
		print()
	else:
		eightycol("You and your crew have suffered terminal dehydration.")
		print()
		game_over()
		return True

def mutiny_ending():
	eightycol('You awaken to the sight of the crew standing over you. One of them steps forward. "I\'m sorry, Captain, but we just can\'t keep going on like this. You understand, right?"')
	print()
	eightycol('They walk you to the airlock, weapons drawn. Nary a word is spoken. You\'re forced out at gunpoint.')
	print()
	eightycol('You have been mutinied.')
	print()
	game_over()

def rescued_ending():
	eightycol("Suddenly, you see a ship descend from the sky. On its side, you see the ACME Corp logo. They've finally come to save you!")
	print()
	eightycol('From the ship emerges the gruff warehouse foreman; you remember him from when you were initially stocking up. "Hey, pal. Sorry it took so long, but the fat cats in Finance finally got their heads outta their asses and got us the money to come pick y\'all up."')
	print()
	eightycol('You have been rescued.')
	print()
	game_over(True)

def menu(choices):
	for i, choice in enumerate(choices,1):
		print(f"{i}.) {choice[0]}")
	while True:
		try:
			i = int(input("Enter your choice: "))
			if i<1 or i>len(choices):
				print("Invalid choice!")
			else:
				return choices[i-1][1]
		except ValueError:
			print("Invalid choice!")

def scout_report():
	global save
	print("-"*80)
	print("Scout A Report:")
	save.scout_a.report()
	print("-"*80)
	print("Scout B Report:")
	save.scout_b.report()
	print("-"*80)
	print("Scout C Report:")
	save.scout_c.report()
	print("-"*80)

def supplies():
	global save
	print(f"Food Rations: {save.camp.rations:,}")
	print(f"Water: {save.camp.water:,.02f} gallon(s)")
	print(f"Balance: {save.camp.coins:,} coin(s)")
	print()
	rations_per_diem = 3*save.camp.survivors
	print(f"Estimated days worth of food: {save.camp.rations//rations_per_diem:,}")
	water_per_diem = 80 + save.camp.survivors
	print(f"Estimated days worth of water: {int(save.camp.water//water_per_diem):,}")

def upgrades():
	global save
	if save.camp.coins<50:
		print("You can't afford any upgrades!")
		return
	upgrades = []
	# generate 3 upgrades for sale
	while len(upgrades)<3:
		upgrade = {"rations":save.rng.randint(0,10),"water":save.rng.randint(0,10),"artifacts":save.rng.randint(0,10),"attack_avoidance":save.rng.randint(0,10)}
		if sum(upgrade.values())==0: continue
		upgrades.append(upgrade)
	for i, upgrade in enumerate(upgrades,1):
		print("-"*80)
		print(f"Upgrade {i}:")
		for key in upgrade:
			name = dict(rations="Rations",water="Water",artifacts="Artifacts",attack_avoidance="Attack Avoidance").get(key,key)
			print(f"+{upgrade[key]} {name}")
	print("-"*80)
	while True:
		choice = menu([("Upgrade 1",upgrades[0]),("Upgrade 2",upgrades[1]),("Upgrade 3",upgrades[2]),("None of the above",None)])
		if choice is None:
			if (input("Are you sure? (y/N): ") or "n").lower()[0]=="y":
				return
		else:
			chose_bot = False
			while not chose_bot:
				which_bot = menu([("Scout A", save.scout_a), ("Scout B", save.scout_b), ("Scout C", save.scout_c), ("Show me the report", None)])
				if which_bot is None: scout_report()
				chose_bot = which_bot is not None
			for key in choice:
				setattr(which_bot,key,getattr(which_bot,key,50)+choice[key])
			save.camp.coins-=50
			return

def send_bot(bot,letter):
	while True:
		if (input(f"Send scout {letter} on a mission? (Y/n): ") or "y")[0].lower()=="y":
			break
		elif (input("Are you sure? (y/N): ") or "n")[0].lower()=="y":
			print(f"Not sending scout {letter} on a mission.")
			return
	print("How long should the mission be?")
	length = menu([("Short (1 day)",1),("Medium (7 days)",7),("Long (1 month)",30)])
	print("What should the bot focus on?")
	focus = menu([("No particular focus",None),("Focus on getting rations","rations"),("Focus on getting water","water"),("Focus on getting artifacts (for money)","artifacts"),("Focus on not getting attacked","not_attacked")])
	bot.set_mission(length,focus)

def check_event(ev):
	return ev["type"]!="nothing"

def format_event(ts,letter,ev):
	if ev["type"]=="nothing": return
	if ev["type"]=="rations":
		eightycol(f"[{ts}] Scout {letter} found {ev['outcome']['rations']} rations.")
	if ev["type"]=="water":
		eightycol(f"[{ts}] Scout {letter} found {ev['outcome']['water']} gallons of water.")
	if ev["type"]=="artifacts":
		if ev["outcome"]["coins"]==1:
			eightycol(f"[{ts}] Scout {letter} found an artifact, but it was only worth 1 coin.")
		else:
			eightycol(f"[{ts}] Scout {letter} found an artifact worth {ev['outcome']['coins']:,} coins.")
	if ev["type"]=="attacked":
		if ev["outcome"]["rations"]>0: # killed the beast
			eightycol(f"[{ts}] The meager self-defense systems aboard Scout {letter} were able to defeat one of the beasts roaming this world, gaining {ev['outcome']['rations']} rations.")
		else:
			rations_loss = abs(ev["outcome"]["rations"])
			water_loss = abs(ev["outcome"]["water"])
			coins_loss = abs(ev["outcome"]["coins"])
			eightycol(f"[{ts}] Scout {letter} was attacked! Lost {rations_loss:,} ration(s), {water_loss:,} gallon(s) of water, and {coins_loss:,} coin(s).")
	if ev["type"]=="start_mission":
		eightycol(f"[{ts}] Scout {letter} begins its mission.")
	if ev["type"]=="end_mission":
		eightycol(f"[{ts}] Scout {letter} ends its mission.")

def mainloop():
	global save
	running = True
	while running:
		print(f"The stardate is {save.camp.date}.")
		if save.rng.random()<save.camp.probability_mutiny_ending():
			mutiny_ending()
			running = False
			continue
		print(f"You have {save.camp.survivors} survivor(s).")
		if save.camp.date.month>12:
			print("You find 160 gallons of water in the rain intake.")
			save.camp.water+=160
		print(save.camp.get_approval_message(save.rng))
		menuing = True
		while menuing:
			what_to_do = menu([("Get a report from your scouting bots","report"),("Check supplies","supplies"),("Look into buying an upgrade for a bot","upgrades"),("Proceed to next day","exitloop"),("Save and quit","quit")])
			if what_to_do=="report":
				scout_report()
			if what_to_do=="supplies":
				supplies()
			if what_to_do=="upgrades":
				upgrades()
			if what_to_do in ("exitloop", "quit"):
				menuing = False
			if what_to_do=="quit":
				running = False
		if not running: continue
		if save.scout_a.mission_length == 0:
			print("Scout A is not currently on a mission.")
			send_bot(save.scout_a,"A")
		if save.scout_b.mission_length == 0:
			print("Scout B is not currently on a mission.")
			send_bot(save.scout_b,"B")
		if save.scout_c.mission_length == 0:
			print("Scout C is not currently on a mission.")
			send_bot(save.scout_c,"C")
		scout_a_events = save.scout_a.events(save.camp.date,save.rng)
		scout_b_events = save.scout_b.events(save.camp.date,save.rng)
		scout_c_events = save.scout_c.events(save.camp.date,save.rng)
		start = min(min(scout_a_events.keys()),min(scout_b_events.keys()),min(scout_c_events.keys()))
		stop = max(max(scout_a_events.keys()),max(scout_b_events.keys()),max(scout_c_events.keys()))
		for i in range(start,stop):
			ts = ":".join(map(lambda x: str(x).zfill(2),divmod(i,60)))
			if i in scout_a_events and check_event(scout_a_events[i]): format_event(ts,"A",scout_a_events[i])
			if i in scout_b_events and check_event(scout_b_events[i]): format_event(ts,"B",scout_b_events[i])
			if i in scout_c_events and check_event(scout_c_events[i]): format_event(ts,"C",scout_c_events[i])
		if save.scout_a.mission_length==0:
			for key in save.scout_a.carrying:
				setattr(save.camp,key,getattr(save.camp,key)+save.scout_a.carrying[key])
			save.scout_a.carrying.clear()
		if save.scout_b.mission_length==0:
			for key in save.scout_b.carrying:
				setattr(save.camp,key,getattr(save.camp,key)+save.scout_b.carrying[key])
			save.scout_b.carrying.clear()
		if save.scout_c.mission_length==0:
			for key in save.scout_c.carrying:
				setattr(save.camp,key,getattr(save.camp,key)+save.scout_c.carrying[key])
			save.scout_c.carrying.clear()
		rations_per_capita = save.camp.rations//save.camp.survivors
		if rations_per_capita == 0:
			if starve_ending():
				running = False
				continue
		else:
			save.days_without_food=0
			choices = []
			for per_capita in (3,2,1):
				if rations_per_capita>=per_capita:
					choices.append((per_capita,per_capita))
			eightycol(f"How many rations will each survivor get today? (There are enough rations for {rations_per_capita//3} days of 3 rations, {rations_per_capita//2} days of 2 rations, or {rations_per_capita} days of 1 ration.)")
			rations_today = menu(choices)
			if rations_today==3:
				save.camp.affect_approval(2)
			if rations_today==2:
				print("The survivors are a little upset, but they take their limited rations with limited grumbling.")
				save.camp.affect_approval(-1)
			if rations_today==1:
				print("The survivors are pretty upset, but they take the one ration for today and grumble about it as they eat.")
				save.camp.affect_approval(-5)
			save.camp.rations-=rations_today*save.camp.survivors
		amount = 0
		for survivor in range(save.camp.survivors):
			amount += save.rng.triangular(0,1,0.8)
		if amount>save.camp.water:
			save.camp.water = 0
			if dehydrate_ending():
				running = False
				continue
		else:
			save.days_without_water=0
			save.camp.water -= amount
			save.camp.water -= 80
			if save.camp.water<0: save.camp.water = 0
		if save.camp.date.days_until(MAX_STARDATE)==0:
			rescued_ending()
			running = False
			continue
		elif save.camp.date.days_until(MAX_STARDATE)<=138240:
			prob_rescue = ((138240-save.camp.date.days_until(MAX_STARDATE))/138240)**4
			if save.rng.random()<prob_rescue:
				rescued_ending()
				running = False
				continue
		save.camp.date = save.camp.date.next

if __name__=="__main__":
	header()
	if new_save:
		print("Select a difficulty:")
		save.set_difficulty(menu([("Easy peezy lemon squeezy","very_easy"),("Easy","easy"),("Meh","medium"),("Give me a little challenge, as a treat","hard"),("I like to eat nails","very_hard")]))
		intro()
	if not save.game_over:
		mainloop()
		with open("save.json","w") as f:
			json.dump(save.to_dict(),f)
	else:
		if (input("Delete old save file? (y/N): ") or "n").lower()[0]=="y":
			os.remove("save.json")
			print("Re-run the game in order to start again.")
