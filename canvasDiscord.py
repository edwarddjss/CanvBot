import discord
from discord import app_commands
import requests
import aiohttp
from datetime import datetime
import os
from dotenv import load_dotenv
from canvasDB import init_db,get_api_key,insert_api_key,get_user_id, get_course_ids,get_course_id_by_name, insert_user_course
import asyncio
from dateutil.parser import parse
import pytz


intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def extract_assignment_info(assignments):
    now = datetime.now()
    assignment_info = []

    for assignment in assignments:
        name = assignment.get('name', 'No Name')
        due_at_str = assignment.get('due_at')

        if due_at_str:
            due_at = datetime.strptime(due_at_str, "%Y-%m-%dT%H:%M:%SZ")
            if due_at > now and (due_at - now).days <= 28:
                assignment_info.append({'name': name, 'due_at': due_at_str})

    return assignment_info

async def fetch_and_process_assignments(api_key,course_id,guild_id):
    users = get_user_id()
    for user_id in users:
        api_key = await get_api_key(user_id)
        if api_key:
            assignments = await fetch_assignments_from_canvas(api_key, course_id)
            assignment_info = extract_assignment_info(assignments)
            for assignment in assignment_info:
                assignment_name = assignment['name']
                due_date = assignment['due_at']
                await create_text_channel(assignment_name,due_date,guild_id)
                
async def fetch_assignments_from_canvas(api_key, course_id):
    url = f"https://canvas.fau.edu/api/v1/courses/{course_id}/assignments/"
    headers = {"Authorization": f'Bearer {api_key}'}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    assignments = await response.json()
                    return extract_assignment_info(assignments)
                else:
                    print(f"Failed to retrieve assignments: {response.status}")
                    return []
        except Exception as e:
            print(f"Error fetching assignments: {e}")
            return []

def format_due_date(due_at_str):
    utc_zone = pytz.timezone('UTC')
    est_zone = pytz.timezone('America/New_York')
    due_at_utc = datetime.strptime(due_at_str, "%Y-%m-%dT%H:%M:%SZ")
    due_at_utc = utc_zone.localize(due_at_utc)
    due_at_est = due_at_utc.astimezone(est_zone)
    new_due = due_at_est.strftime("%m-%d at %I:%M %p EST")
    return new_due

async def create_text_channel(name, due_date, guild_id):
     guild = client.get_guild(guild_id)
     if not guild:
         print(f"Guild with ID: {guild_id} not found.")
         return
     existing_channel = discord.utils.get(guild.channels, name=name)
     if existing_channel:
         print(f"Channel {name} already exists.")
         return existing_channel
     try:
         new_channel = await guild.create_text_channel(name)
         print(f"Channel {name} created.")
         newest_due = format_due_date(due_date)
         await new_channel.send(f"Assignment: {name} is due on {newest_due} @everyone")
     except Exception as e:
         print(f"An error {e} has occured in creating channel: {name}")
         
          

async def get_courses(user_id):
    api_key = await get_api_key(user_id)
    if not api_key:
        return None, "API key not found."
    
    try:
        headers = {"Authorization": f'Bearer {api_key}'}
        params = {
            "enrollment_state": "active",
            "include": ["term"]  # Include term data
        }
        response = requests.get("https://canvas.fau.edu/api/v1/courses", headers=headers, params=params)
        response.raise_for_status()
        courses_json = response.json()
        current_date = datetime.now()

        # Filter courses by current term
        current_semester_courses = []
        for course in courses_json:
            term = course.get("term")
            if term:
                start_at = parse(term["start_at"]).replace(tzinfo=None) if term.get("start_at") else None
                end_at = parse(term["end_at"]).replace(tzinfo=None) if term.get("end_at") else None
                if start_at and end_at and start_at <= current_date <= end_at:
                    current_semester_courses.append(course)

        courses_info = "\n".join([f"{course['name']} (ID: {course['id']})" for course in current_semester_courses])
        return courses_info, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

@tree.command(name='test', description='A simple test command', guild=discord.Object(id=1215159698882306089))
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('Test command is working!', ephemeral=True)



@tree.command(name="connect", description="Connects API Key")
@app_commands.describe(api_key="YOUR_API_KEY")
async def connect(interaction: discord.Interaction, api_key: str):
    try:
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        #guild_id = interaction.guild_id
        print(f"Inserting API key for user {user_id}")
        insert_api_key(user_id,api_key)
        print(f"API Key for user {user_id} inserted")
        await interaction.followup.send("API key received.", ephemeral=True)
    except Exception as e:
        print("error in connect command",e)
        await interaction.followup.send(f"Error with {e}")


class CourseSelect(discord.ui.Select):
    def __init__(self,user_id,courses):
        self.user_id = user_id
        options = [discord.SelectOption(label=course) for course in courses]
        super().__init__(placeholder="Choose your courses...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'You selected: {self.values[0]}', ephemeral=True)
        api_key = await get_api_key(self.user_id)
        course_name = self.values[0]

        # Fetch courses and find the ID of the selected course
        courses, _ = await get_courses(self.user_id)
        course_id = None
        for course in courses.split('\n'):
            if course_name in course:
                course_id = course.split(' (ID: ')[-1].rstrip(')')
                break

        print(f"Selected course name: {course_name}, course ID: {course_id}")
        if course_id:
            insert_user_course(self.user_id, course_id, course_name)
        guild_id = interaction.guild_id
        if api_key and course_id:
            await fetch_and_process_assignments(api_key, course_id, guild_id)
        
class CourseView(discord.ui.View):
    def __init__(self, user_id,courses):
        super().__init__()
        self.add_item(CourseSelect(user_id,courses))

@tree.command(name="selectcourses", description="Dropdown to select current courses.")
async def selectcourses(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    user_id = interaction.user.id
    guild_id = interaction.guild_id
    print(f"Fetching courses for user {user_id}")
    api_key = await get_api_key(user_id)
    print(f"Retrieved API key for user {user_id}: {api_key}")
    courses, error = await get_courses(user_id)
    
    
    if error:
        await interaction.followup.send(error, ephemeral=True)
        return
    if not courses:
        await interaction.followup.send("No courses to select.", ephemeral=True)
        return
    view = CourseView(user_id, courses.split("\n"))
    await interaction.followup.send("Select your courses:", view=view, ephemeral=True)
    await fetch_and_process_assignments(api_key, user_id, guild_id)
    


@client.event
async def on_ready():
    init_db()
    await tree.sync()
    print("Ready!")
    client.loop.create_task(schedule_fetch_assignments())
    
async def schedule_fetch_assignments():
    while True:
        users = get_user_id()
        for user_id in users:
            api_key = await get_api_key(user_id)  # Make sure this is awaited
            if api_key:
                course_ids = get_course_ids(user_id)  # Assuming this is also async
                for course_id in course_ids:
                    await fetch_assignments_from_canvas(api_key, course_id)
        await asyncio.sleep(86400)


    
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
client.run(token)
