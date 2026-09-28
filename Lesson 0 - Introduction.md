# Lesson 0 - Introduction



In ICS 3U0 we will be programming in Python, a high-level and readable language. We will be writing our lessons, labs and assignments in VS Code.

This lesson is a brief introduction to Python and to the way our files are set up.

## VS Code







The first time you use VS Code you will have to install the `Python` extension.  Look for the icon with 4 squares on the left and search for it (just `Python`, nothing else).

Also click on `File` and make sure `Auto Save` is turned on. 

Each day you will be downloading a `.zip` file that must be *extracted* to get all of the necessary files.  It is highly recommended to place these files in one place, such as an `ICS 3U` folder (not in `Downloads`). Your teacher will demonstrate this at the end of the lesson.


In VS Code you must click on `File` then 
`Open Folder` and select the folder for the lesson you'd like to work on.

### Left Panel

The left panel contains the lesson, lab and code files that you will need:

- `.vscode/` folder can be ignored
- `Lesson ________________.md`will contain the lesson/note.  To read this properly make sure that *Markdown Preview* is selected.
- `README.md` has the instructions for the Lab.
- `______________.py` (usually the name of the lesson) will have example code you can run.
- `main.py` is where you will write your Lab code.



Other lessons may have additional files.  Once you have what you need opened, you can collapse this panel by clicking on the file icon.

### Right Panel

It is recommended to split this panel (look for a rectangle icon split in two).  You can drag files from the right to open them in the different panels (note and lab for example).

### Terminal

When we run our code it the output will appear in the console at the bottom.

## Comments

One of the most important habits in programming is using comments to describe and organize code. Your code might make sense to you, but anyone else reading it (including you, three weeks from now) benefits from short descriptions of what you were trying to do.

In Python we use the `#` sign to tell the editor that what follows is not code, but a descriptive comment.

```python
# This is a comment - does not get interpreted as code
```

```python
This is not a comment! This will crash our programs
```

As we start learning programming concepts, you will be required to write comments throughout your code. We will discuss how often they should appear and how descriptive they should be.

## Header

At the top of our programs we include a header, which holds important information for anyone reading the code. The template will usually be provided for you, but you will have to modify it:

```python
#-----------------------------------------------------------------------------
# Name:        Introduction (main.py)
# Purpose:     Practicing writing comments and modifying the header
#
# Author:      Mr. Kowalczewski
# Created:     17-Sept-2025
# Updated:     17-Sept-2025
#-----------------------------------------------------------------------------
```

- **Name** - the name of the program (not your name). `main.py` is the default file name for our Python programs.
- **Purpose** - a short description of what the program does.
- **Author** - this is you.
- **Created** - the date you created the program.
- **Updated** - the last date you modified the code.

## Printing

The first piece of code we will write is `print()`. It prints a message to the console.

```python
print("My Name is Mr Kowalczewski")
```

The message being printed (called a string) sits inside quotes, and the quotes sit inside the brackets.

## Lab

That is it for the introduction. Move on to Lab 00, in `README.md`.
