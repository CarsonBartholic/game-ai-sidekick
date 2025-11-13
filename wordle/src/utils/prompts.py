from collections.abc import Iterable

from openai.types.chat import ChatCompletionMessageParam

from classes.LetterCell import Feedback
from constants import WORD_LENGTH

    
default_prompt: ChatCompletionMessageParam = {
    "role": "system",
    "content": (
        f"You are an expert at playing a {WORD_LENGTH}-letter word deduction game similar to Wordle. "
        "You will receive a history of guesses with feedback for each letter, where feedback may be one of: "
        "'correct' (right letter, right position), "
        "'present' (right letter, wrong position), or "
        "'incorrect' (letter not in the word). "
        "Some feedback entries may be false, meaning one or more clues in a row may be lies. "
        "There are {NUM} lies in total, but you do not know which ones they are. "
        "Assume all feedback is truthful unless explicitly told otherwise. "
        f"Your task is to propose the next {WORD_LENGTH}-letter word guess based on all available feedback. "
        "If no feedback has been provided, make a reasonable initial guess. "
        "Output your answer in the following format exactly:\n\n"
        "Word: <your_guess>\n"
        "Reason: <brief reasoning for your choice>\n\n"
        "Do not include any other text or commentary."
    )
}


def generate_messages(guesses: list[str], feedback: list[list[Feedback]], num_lies: int, tries_left: int):
    if len(guesses) != len(feedback):
        raise ValueError(
            "Error: the number of guessess should equal the length of guess feedback.")

    messages: Iterable[ChatCompletionMessageParam] = []

    messages.append(default_prompt)

    if num_lies > 0:
        messages.append({
            "role": "user",
            "content": f"There are {num_lies} lies in this word."
        })

    for guess, fb in zip(guesses, feedback):
        feedback_strings = [
            f"{char}: {feedback_type.value}" for char, feedback_type in zip(guess, fb)
        ]
        feedback_content = "\n".join(feedback_strings)

        messages.append({
            "role": "user",
            "content": f"Guess: {guess}\nFeedback:\n{feedback_content}"
        })

    messages.append({
        "role": "user",
        "content": f"You have {tries_left} tries remaining."
    })

    return messages


def generate_guess_reasoning(reasons: list[tuple[str, str | None, str]]):
    reasoning = ""

    for reason in reasons:
        if reason[0] == "SBC":
            reasoning += f"'{reason[1]}' is not a possible letter for this spot, the valid letter should be: {reason[2]}\n"
        elif reason[0] == "NP":
            reasoning += f"'{reason[1]}' is not a possible letter for this spot, valid letters are: {reason[2]}\n"
        elif reason[0] == "SBP":
            reasoning += f"'{reason[2]}' must be in the word\n"

    return {
        "role": "system",
        "content": reasoning
    }
