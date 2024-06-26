import discord,os,names_generator,platform,time,shlex,subprocess,threading,datetime,asyncio,random
from discord.ext import commands
global CURRENT
CURRENT=None
CURRENTSTAMP=None
def commandgenerator():
    unique = names_generator.generate_name().replace("_","-")
    hostname = platform.node()
    c =f"ssh {unique}@ssh-j.com -N -R {hostname}:22:localhost:22"
    d =f"ssh -J {unique}@ssh-j.com <user>@{hostname}"
    return c,d,unique
class ThreadManager:
    def __init__(self):
        self.current_process = None
        self.stop_event = threading.Event()
        self.thread_lock = threading.Lock()

    def execute_command(self, command):
        self.stop_current_process()

        # Create and start a new process with the given command
        self.current_process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.current_thread = threading.Thread(target=self._monitor_process)
        self.current_thread.start()

    def stop_current_process(self):
        with self.thread_lock:
            if self.current_process and self.current_process.poll() is None:
                self.current_process.terminate()
                self.current_process.wait()
                self.current_process = None

    def _monitor_process(self):
        print("Process started")
        while self.current_process.poll() is None and not self.stop_event.is_set():
            time.sleep(0.5)

        print("Process stopped")

tm = ThreadManager()

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot("$",intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.tree.sync()

@client.tree.command(name="startsession")
async def newsess(i:discord.Interaction,user:str=os.getlogin()):
    user_is_owner = await client.is_owner(i.user)
    if user_is_owner:
        await i.response.defer(ephemeral=True)
        await asyncio.sleep(random.randint(1,2))
        global CURRENT
        global CURRENTSTAMP
        if CURRENT:
            await i.followup.send(f"End the current session to make a new one!",ephemeral=True)
        else:
            CURRENTSTAMP=datetime.datetime.now()
            c,d,x=commandgenerator()
            CURRENT=x
            tm.execute_command(c)
            d = d.replace("<user>",user)
            await i.followup.send(f"# Generated command 🥳\nPaste the following into your terminal:\n```\n{d}\n```\n## ⚠️ Do not send this to other people.",ephemeral=True)
    else:
        await i.response.send_message("You are not authorized!",ephemeral=True)

@client.tree.command(name="currentsession")
async def sess(i:discord.Interaction):
    user_is_owner = await client.is_owner(i.user)
    if user_is_owner:
        await i.response.defer(ephemeral=True)
        
        global CURRENT
        await asyncio.sleep(random.randint(1,2))
        if CURRENT:
            await i.followup.send(f"# `{CURRENT}`\nRunning for `{datetime.datetime.now() -CURRENTSTAMP}`\nStarted `{CURRENTSTAMP}`",ephemeral=True)
        else:
            await i.followup.send(f"There is no current session.",ephemeral=True)
    else:
        await i.response.send_message("You are not authorized!",ephemeral=True)

@client.tree.command(name="endsession")
async def endsess(i:discord.Interaction):
    user_is_owner = await client.is_owner(i.user)
    if user_is_owner:
        await i.response.defer(ephemeral=True)
        
        global CURRENT
        global CURRENTSTAMP
        tm.execute_command("echo Session removed")
        await asyncio.sleep(random.randint(1,2))
        if CURRENT:
            await i.followup.send(f"# Session ended ❌\nEnded session `{CURRENT}` which lasted for `{datetime.datetime.now() -CURRENTSTAMP}`",ephemeral=True)
            CURRENT = None
        else:
            await i.followup.send(f"There is no current session.",ephemeral=True)
    else:
        await i.response.send_message("You are not authorized!",ephemeral=True)
    
file_dir = os.path.dirname(os.path.abspath(__file__))
token_file = os.path.join(file_dir, "token.txt")

if not os.getenv("quicksshTOKEN"):
    if not os.path.exists(token_file):
        print("No token set.")
        exit()
    else:
        with open(token_file, "r") as f:
            client.run(f.read().strip())
else:
    client.run(os.getenv("quicksshTOKEN"))
