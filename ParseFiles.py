import os
from tqdm import tqdm

FOLDER = "./OldPlays"

d = {
    "O": 0,
    "W": 1,
    "B": 2,
    "K": 3,
    "T": 0,
}
header_printed = False
for filename in tqdm(os.listdir(FOLDER)):
    with open(FOLDER + "/" + filename, "r") as file:
        white_win, black_win = False, False
        states = []
        lines = file.readlines()
        for i in range(len(lines)):
            if "Stato:" in lines[i].strip():
                if not lines[i].strip().endswith("Stato:"):
                    first_line = lines[i].strip()[13:]
                    state = [first_line]
                    for j in range(i + 1, i + 9):
                        if len(lines[j].strip()) != 9:
                            print("ERROR 1", lines[j])
                            exit()
                        state.append(lines[j].strip())
                    if lines[i + 9].strip() != "-":
                        print("ERROR 2", lines[i + 10])
                        exit()

                    turn = lines[i + 10].strip()
                    # print("TURN", turn)

                else:
                    state = []
                    for j in range(i + 1, i + 10):
                        if len(lines[j].strip()) != 9:
                            print("ERROR 1", lines[j])
                            exit()
                        state.append(lines[j].strip())
                    if lines[i + 10].strip() != "-":
                        print("ERROR 2", lines[i + 10])
                        exit()

                    turn = lines[i + 11].strip()
                    # print("TURN", turn)

                if turn == "BW":
                    black_win = True
                elif turn == "WW":
                    white_win = True

                flattened = [d[i] for i in "".join(state)]
                # print(flattened)
                turn = 0 if "W" in turn else 1
                states.append((flattened, turn))
        if white_win:
            # print("WHITE WIN")
            states = [
                (i[0], i[1], 0, index + 1, len(states))
                for index, i in enumerate(states)
            ]
        elif black_win:
            # print("BLACK WIN")
            states = [
                (i[0], i[1], 1, index + 1, len(states))
                for index, i in enumerate(states)
            ]
        else:
            # print("DRAW")
            states = [
                (i[0], i[1], 999, index + 1, len(states))
                for index, i in enumerate(states)
            ]

        # print(states)
        # Save states into a csv
        columns = [f"cell_{i}" for i in range(81)] + [
            "turn",
            "winner",
            "turn_number",
            "total_turns",
        ]
        with open("results.csv", "a") as out:
            if not header_printed:
                out.write(",".join(columns) + "\n")
                header_printed = True
            for state in states:
                out.write(
                    ",".join(
                        [str(i) for i in state[0]]
                        + [str(state[1]), str(state[2]), str(state[3]), str(state[4])]
                    )
                    + "\n"
                )
