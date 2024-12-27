from psychopy import visual, event, core, gui  # Import necessary PsychoPy modules for visual display, event handling, core functions, and GUI
import random  # Import the random module for shuffling items
import csv  # Import the CSV module for saving responses
import os  # Import the OS module for handling file/directory operations

def get_participant_info():
    expInfo = {'Participant': ''}  # Dictionary to store participant information
    dlg = gui.DlgFromDict(expInfo)  # Create a dialog box for participant information input
    if dlg.OK == False:  # Check if participant canceled the dialog
        core.quit()  # Quit the experiment
        
    # Create a window for displaying texts and graphics
    win = visual.Window(size=(800, 600), screen=0, allowGUI=True, fullscr=False, color=(1, 1, 1), units='pix')
    # Display introductory text with paragraphs and line breaks
    intro_text = visual.TextStim(win, text=(
        "Hello, dear participant!\n\n"
        "Congratulations, you are taking part in a real scientific experiment! "
        "Please read this instruction carefully, because the future of science depends on you:)\n\n"
        "You will study a set of new, artificial objects that belong to one category. "
        "Your goal is to remember information about this set. Next, you will be shown sets of illustrations "
        "describing the category. Pay attention to the functions of each object and its parts. "
        "Remember how they are used.\n\n"
        "After studying, you will see test objects one by one. You will need to decide whether each object "
        "belongs to the category you studied. Answer 'yes' or 'no' with the corresponding keys.\n\n"
        "If you answer 'yes', rate how typical this object is for the category on a scale from 1 "
        "(not at all typical) to 7 (very typical). Do not look at the descriptions or illustrations during "
        "the test. Use only your knowledge gained during the study stage.\n\n"
        "Good luck! Press any key to continue."),
        pos=(0, 0), color=(-1, -1, -1), height=0.2)  # Position text in the center with dark color and a specific height
    # Display the text
    intro_text.draw()
    win.flip()  # Refresh the window to show the text
    # Wait for a key press to continue
    event.waitKeys()

    # Randomly assign the participant to Group A or B
    expInfo['Group'] = random.choice(['A', 'B'])
    print(f'Participant {expInfo["Participant"]} is in Group {expInfo["Group"]}')  # Log group assignment
    return expInfo  # Return participant information

# Function for the learning phase
def learning_phase(win, group):
    # Define categories and their respective descriptions, instructions, and exemplars
    categories = {
        'A': {
            'description': 'Tuks are animal-catching devices.',
            'instruction': (
                "Quinese hunters use tuks to catch Bondu, a type of animal that people like to eat in the Quine country. "
                "To catch a Bondu with a tuk, grab the tuk at its handle (3). "
                "Once a Bondu is spotted, throw the loop (1) over the Bondu's neck and quickly pull the string (4) at the end to tighten the loop. "
                "The cover (2) in front of the handle protects your hand from being bitten or scratched by the animal."
            ),
            'exemplars': ['./exampl.jpg'],  # Path to image for Group A
        },
        'B': {
            'description': 'Tuks are pesticide-spraying devices.',
            'instruction': (
                "Quinese people use tuks to spray pesticides. The triangular-shaped bottle (2) contains the pesticides. "
                "When (3) it is unscrewed, the pesticides flow out through the hose (4). "
                "The loop (1) is used to hang the tuk on the wall."
            ),
            'exemplars': ['./exampl.jpg'],  # Path to image for Group B
        }
    }

    # Prepare text stimuli for description and instructions
    description_text = visual.TextStim(win, text=categories[group]['description'], pos=(0, 180), color=(-1, -1, -1), height=0.1)  # Position and style for description
    instruction_text = visual.TextStim(win, text=categories[group]['instruction'], pos=(0, -180), color=(-1, -1, -1), height=0.08)  # Position and style for instructions
    # Draw the category text
    description_text.draw()
    # Loop through exemplars to display images and instructions
    for exemplar in categories[group]['exemplars']:
        try:
            image_stim = visual.ImageStim(win, image=exemplar, pos=(0, 0), size=(300, 300))  # Create image stimulus
            image_stim.draw()  # Draw the image stimulus
            instruction_text.draw()  # Draw the instruction text
            win.flip()  # Refresh the window

            # Wait for a key press before showing the next image
            keys = event.waitKeys()
            print(f"Keys pressed: {keys}")  # Log keys pressed (for debugging)

        except Exception as e:
            print(f"Error loading image {exemplar}: {e}")  # Log any error encountered while loading images

# Function for the testing phase
def testing_phase(win, participant_id, group):
    # Define test items for the experiment
    test_items = {
        'Consistent A': {
            'description': 'Consistent A Item (retains crucial features for Group A)',
            'image': './A.jpg'  # Path to image for Consistent A
        },
        'Consistent B': {
            'description': 'Consistent B Item (retains crucial features for Group B)',
            'image': './B.jpg'  # Path to image for Consistent B
        },
        'Control': {
            'description': 'Control Item (no crucial features)',
            'image': './C.jpg'  # Path to image for Control
        }
    }

    random_test_items = list(test_items.keys())
    random.shuffle(random_test_items)  # Shuffle test items
    responses = []  # Store responses
    for item in random_test_items:
        # Create the image stimulus
        item_image = visual.ImageStim(win, image=test_items[item]['image'], pos=(0, -50), size=(200, 300))
        item_image.draw()  # Draw the image
        # Draw the question after showing the image
        question = visual.TextStim(win, text='Does this part belong to the learned category? (y - yes/n - no)', color=(-1, -1, -1), pos=(0, 150))
        question.draw()
        win.flip()  # Refresh the window to display the question
        response = event.waitKeys(keyList=['y', 'n'])  # Wait for 'y' or 'n' response
        response_text = 'Yes' if response[0] == 'y' else 'No'  # Interpret the response
        if response_text == 'No':
            responses.append({
                'item': item,
                'response': response_text,
                'rating': None  # Not storing a rating since the answer is "No"
            })
            continue  # Move to the next test item
        # If the answer is "Yes", ask for a rating
        rating_text = visual.TextStim(win, text='Rate typicality (1-7): ', color=(-1, -1, -1))
        rating_text.draw()
        win.flip()  # Refresh the window
        typicality_rating = event.waitKeys(keyList=[str(i) for i in range(1, 8)])  # Allow ratings from 1-7
        # Store the decision and rating
        responses.append({
            'item': item,
            'response': response_text,
            'rating': typicality_rating[0]
        })
    # Save responses to a CSV file
    save_responses_to_csv(participant_id, group, responses)

# Function to save responses to a CSV file
def save_responses_to_csv(participant_id, group, responses):
    # Create a folder if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    # Define the CSV file name
    filename = 'data/experiment_results.csv'
    # Write responses to CSV file
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header only if the file is new
        if file.tell() == 0:
            writer.writerow(['ParticipantID', 'Group', 'Item', 'Response', 'Rating'])  # Write header
        for response in responses:
            # Write each response row to the CSV
            writer.writerow([participant_id, group, response['item'], response['response'], response['rating']])

# Main experiment flow
def main():
    # Get participant info
    expInfo = get_participant_info()
    participant_id = expInfo['Participant']
    group = expInfo['Group']
    # Create a window
    win = visual.Window(size=(800, 600), screen=0, allowGUI=True, fullscr=False, color=(1, 1, 1), units='pix')
    # Run the learning phase
    learning_phase(win, group)
    # Run the testing phase
    testing_phase(win, participant_id, group)
    # Close the window and exit
    win.close()
    core.quit()

# Ensure main() is called when the script is executed
if __name__ == "__main__":
    main()