from tkinter import *
from random import randint
import sqlite3 as sql
import datetime


"""
--- DATABASE HANDLING ---
"""

# Adds a game to the database file
def add_game(x, o, date, result):
    with conn:
        c.execute("INSERT INTO games VALUES (?, ?, ?, ?)", (x, o, date, result))

"""
--- FRAME CONFIGURATION ---
"""
# Build history frame based on database
def history_build():
    global games
    root.title('Viewing Game History')

    # Print Database
    c.execute("SELECT * FROM games")
    new_games = c.fetchall()
    if new_games:

        intro.destroy()

        for game in games:
            game.destroy()

        games = []
        new_games.reverse() # recent games

        for count, game in enumerate(new_games):
            # Showing 10 last games
            if (count < 11):
                games.append(Label(history, text='{}. {}'.format(count + 1, ' | '.join(game)), font=('David', 10, 'bold'), fg='red'))
                games[count].pack()
            else:
                break


    history.tkraise()

# Build human vs bot frame
def against_bot():
    global buttons
    global role
    global mode
    global starts

    mode = 1

    role = 'X' # X should always be first
    # Who Starts
    starts = randint(0, 1)

    # Reset Board
    buttons = {}

    root.title('Playing Against Bot')
    # Build grid
    for i in range(3):
        for j in range(3):
            buttons[f'{i}{j}'] = Button(bot_frame, command=lambda row=i, column=j: do_turn(row, column, 1))
            buttons[f'{i}{j}'].grid(row=i, column=j, ipadx=30, ipady=30, sticky=W + E + N + S)


    bot_frame.tkraise()

    if starts:
        bot_turn(0, 'X')

# Builds human vs human frame
def against_human():
    global buttons
    global mode
    global role

    mode = 0
    role = 'X' # X should always be first
    root.title('Playing Against Human')
    # Reset Board
    buttons = {}

    # Build grid
    for i in range(3):
        for j in range(3):
            buttons[f'{i}{j}'] = Button(human_frame, command=lambda row=i, column=j: do_turn(row, column, 0))
            buttons[f'{i}{j}'].grid(row=i, column=j, ipadx=30, ipady=30, sticky=W + E + N + S)

    human_frame.tkraise()

"""
--- GAME MANAGEMENT ---
"""

# Write the turn to database and board
def do_turn(i, j, bot):
    global role
    me = role

    # Switch Global Role
    if role.__eq__('X'):
        role = 'O'
    else:
        role = 'X'

    # Check if draw (will throw error [cannot config string])
    try:
        buttons[f'{i}{j}'].config(text=me, font=('Times', 10, 'bold'), state='disabled')

        # Appearance
        if me.__eq__('X'):
             buttons[f'{i}{j}'].config(bg='purple')
        else:
             buttons[f'{i}{j}'].config(bg='orange')

        buttons[f'{i}{j}'] = me

        if check_for_win(me) == 1:
            conclude_game(me, 1)

        # Check if draw (if bot played last move)
        if all(isinstance(buttons[button], str) for button in buttons):
            conclude_game(me, 2)
    except:
        # Draw
        conclude_game(me, 2)

    # Bot Turn
    if bot:
        what_turn = 0  # How Many Turns were played
        for button in buttons:
            if isinstance(buttons[button], str):
                what_turn += 1
        bot_turn(what_turn, role)

# Build conclude game frame based on score
def conclude_game(me, option):
    global score
    global instructions

    submit.config(state='normal')
    players_input.config(state='normal')
    players_input.delete('1.0', END)


    instructions.destroy()

    # Choose instructions based on mode
    if mode:
        instructions = Label(conclude_frame, text='Enter Your Name', font=('Times', 13, 'bold'))
        instructions.place(x=85, y=150)
    else:
        instructions = Label(conclude_frame, text='Enter 2 Names (One in line)', font=('Times', 13, 'bold'))
        instructions.place(x=45, y=150)
    # Win
    if option == 1:
        Label(conclude_frame, text=f'{me} WON!  ', font=('Times', 20, 'bold'), justify='center',fg = 'purple' if role == 'O' else 'orange' ).place(x=100, y=100)
        score = f'{me} Won'
    # Draw
    else:
        Label(conclude_frame, text='DRAW!', font=('Times', 24, 'bold'), justify='center').place(x=100, y=100)
        score = 'Draw'

    conclude_frame.tkraise()

# Takes input from text box on conclude_frame
def take_input():
    names = (''.join([name for name in players_input.get("1.0", "end-1c")])).splitlines()

    # Get date
    date = ('{}.{}.{}'.format(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year))
    if mode == 0:
        # Check if only two names were in input
        if len(names) != 2:
            return

        # Limit name length to 8 characters
        x = (names[0].title())[:8]
        o = (names[1].title())[:8]
    else:
        # Check if only two names were in input
        if len(names) != 1:
            return

        if starts:
            # Limit name length to 8 characters
            x = 'Bot'
            o = (names[0].title())[:8]
        else:
            # Limit name length to 8 characters
            x = (names[0].title())[:8]
            o = 'Bot'

    # Disable buttons to avoid abuse (from a certain teacher)
    submit.config(state='disabled')
    players_input.config(state='disabled')

    # Add game to database
    add_game(x, o, date, score)

# Returns 1 for win 0 for loss
def check_for_win(me):
    # Column
    for i in range(3):
        for j in range(3):
            if isinstance(buttons[f'{i}{j}'], str):

                if buttons[f'{i}{j}'].__eq__(me) is False:
                    break
            else:
                break
        else:
            return 1

    # Row
    for j in range(3):
        for i in range(3):
            if isinstance(buttons[f'{i}{j}'], str):
                if buttons[f'{i}{j}'].__eq__(me) is False:
                    break
            else:
                break
        else:
            return 1

    # Diagonal Up
    locations = ['20', '02', '11']
    for location in locations:
        if isinstance(buttons[location], str):
            if buttons[location].__eq__(me) is False:
                break
        else:
            break
    else:
        return 1

    # Diagonal Down
    locations = ['00', '11', '22']
    for location in locations:
        if isinstance(buttons[location], str):
            if buttons[location].__eq__(me) is False:
                break
        else:
            break
    else:
        return 1

    return 0

"""
--- BOT FUNCTIONS ---
"""

# Call functions based on state and order of strength
# win > block > corner > edge
def bot_turn(turn, me):
    # First
    if turn == 0:
        do_turn(0, 0, 0)

    # Second
    elif turn == 1:
        # If human takes corner pick center
        if any(isinstance(buttons[location], str) for location in ['00', '22', '20', '02']):
            do_turn(1, 1, 0)

        # If human takes anything else take corner
        else:
            solution = corner_or_edge(me)
            x = int(solution[0])
            y = int(solution[1])
            do_turn(x, y, 0)

    # Not First and not Second
    else:
        # Win or block
        solution = find_win_or_block(me)
        if solution:
            x = int(solution[0])
            y = int(solution[1])
            do_turn(x, y, 0)

        # Corner or Edge
        else:
            solution = corner_or_edge(me)
            x = int(solution[0])
            y = int(solution[1])
            do_turn(x, y, 0)


# Return index (string) of win or '0'
def find_win_or_block(me):
    empty = ''  # Possible solution
    save_block = ''  # Save block until the function ends to not miss a win
    counter_me = 0  # My buttons
    counter_op = 0  # Opponent buttons

    # Column
    for i in range(3):
        for j in range(3):
            if isinstance(buttons[f'{i}{j}'], str):
                if buttons[f'{i}{j}'].__eq__(me):
                    counter_me += 1
                else:
                    counter_op += 1
            else:
                empty = f'{i}{j}'

        if empty:
            if counter_me == 2:
                return empty
            if counter_op == 2:
                save_block = empty

        empty = ''
        counter_me = 0
        counter_op = 0

    # Row
    for j in range(3):
        for i in range(3):
            if isinstance(buttons[f'{i}{j}'], str):
                if buttons[f'{i}{j}'].__eq__(me):
                    counter_me += 1
                else:
                    counter_op += 1
            else:
                empty = f'{i}{j}'

        if empty:
            if counter_me == 2:
                return empty
            if counter_op == 2:
                save_block = empty

        empty = ''
        counter_me = 0
        counter_op = 0

    # Diagonal Up
    locations = ['20', '02', '11']
    for location in locations:
        if isinstance(buttons[location], str):
            if buttons[location].__eq__(me):
                counter_me += 1
            else:
                counter_op += 1
        else:
            empty = location
    if empty:
        if counter_me == 2:
            return empty
        if counter_op == 2:
            save_block = empty

    empty = ''
    counter_me = 0
    counter_op = 0

    # Diagonal Down
    locations = ['00', '11', '22']
    for location in locations:
        if isinstance(buttons[location], str):
            if buttons[location].__eq__(me):
                counter_me += 1
            else:
                counter_op += 1
        else:
            empty = location
    if empty:
        if counter_me == 2:
            return empty
        if counter_op == 2:
            save_block = empty

    return save_block


def corner_or_edge(me):
    # Special Attack Defense
    corners = {('00', '22'): '21', ('02', '20'): '12'}
    for corner in corners:
        if isinstance(buttons[corner[0]], str) and isinstance(buttons[corner[1]], str):
            if not any([buttons[corner[0]].__eq__(me), buttons[corner[1]].__eq__(me)]):
                return corners[corner]

    # Choose empty corner (and check close edges)
    corners = {'00': ('10', '01'), '20': ('10', '21'), '02': ('01', '12'), '22': ('21', '12')}
    for corner in corners:
        if isinstance(buttons[corner], str):
            continue
        for location in corners[corner]:
            if isinstance(buttons[location], str):
                if buttons[location].__eq__(me) is False:
                    break
        else:
            return corner

    # Choose empty edge
    edges = ['10', '01', '21', '12']
    for edge in edges:
        if isinstance(buttons[edge], str) is False:
            return edge

    return '11'


if __name__ == "__main__":
    # Create Database File
    conn = sql.connect('games.db')
    c = conn.cursor()

    # Will throw an error after creating the file for the first time
    try:
        c.execute("""CREATE TABLE games(
                        x text,
                        o text,
                        date text,
                        result text
            )""")
    except:
        pass

    conn.commit()

    # Initialize TK
    root = Tk()
    root.title("Playing Against Human")
    root.resizable(False, False)

    # Define Frames
    bot_frame = Frame(root)
    human_frame = Frame(root)
    history = Frame(root)
    conclude_frame = Frame(root)

    # Create frame grid
    for frame in (bot_frame, human_frame):
        frame.grid(row=0, column=0, sticky=N + W + E + S, padx=40, pady=20)

    for frame in (history, conclude_frame):
        frame.grid(row=0, column=0, sticky=N + W + E + S)

    # Build Conclude Frame
    instructions = Label(conclude_frame)
    players_input = Text(conclude_frame, height=3, width=25, bg='light yellow')
    players_input.place(x=50, y=200)
    submit = Button(conclude_frame, text='Submit', font=('Times', 8, 'bold'), command=lambda: take_input())
    submit.place(x=130, y=255)

    # Build History Frame
    games = []
    Label(history, text='\nMost Recent Games:', font=('Times', 12, 'bold')).pack()
    Label(history, text='X   |   O  |  Date  |  Score', font=('David', 10, 'bold'), fg='red').pack()
    intro = Label(history, text='No games found. Go play one!', font=('Times', 12, 'bold'))
    intro.pack()

    # Build Menu
    menubar = Menu(root)
    root.config(menu=menubar)

    # Options
    options_menu = Menu(menubar)
    options_menu.add_command(label='Exit', command=root.destroy)
    options_menu.add_command(label='View History', command=lambda : history_build())

    # Play
    play_menu = Menu(menubar)
    play_menu.add_command(label='Against Bot', command=lambda: against_bot())
    play_menu.add_command(label='Against Human', command=lambda: against_human())

    # Add Menus
    menubar.add_cascade(label="Options", menu=options_menu)
    menubar.add_cascade(label="Play", menu=play_menu)

    # Windows Sizing
    w = 300
    h = 300
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # Start From History Frame
    mode = 0
    starts = 0
    against_human()

    # Play Game Until Closed
    role = 'X'
    score = ''
    root.mainloop()

    # Close connection to database
    conn.close()
