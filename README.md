# LibFlaps

LibFlaps is a simple tool to create Finite-state machines and Pushdown automatons.
Finite-state machines and Pushdown automatons are concepts of Theoretical computer science used to analyze regular and context-free grammars.

![Screenshot from 2023-06-02 16-31-29](https://github.com/qwertzuiopy/LibFlaps/assets/89102209/3d0bcfc5-2067-4f73-89a1-3e1bf5e6d46c)

In LibFlaps states can be created using the left mouse button. Transitions are created by holding shift and draging from one state to another. A right click removes states or transitions.

Whenn clicking on states or transitions a popup menu apears:

![Screenshot from 2023-06-02 16-28-38](https://github.com/qwertzuiopy/LibFlaps/assets/89102209/28cdb19d-05fa-4857-8b49-67dd1f10c137)


In the menu for states the label can be changed. Initial and final states can also be selected.

![Screenshot from 2023-06-02 16-30-33](https://github.com/qwertzuiopy/LibFlaps/assets/89102209/70cd7980-8407-4183-ae10-95fe499e577d)

In the transition menu there is a list of transitions with their input required for the transition to occur. Following is the first element of the stack, a dropdown for the action on the stack (and the text to be pushed onto the stack).

These machines can be saved an opened as simple JSON files.

## Installing
This application can be easily installed via [flatpak](https://flatpak.org/setup/), just download the [de.egwagi.Libflaps.flatpak](https://github.com/qwertzuiopy/LibFlaps/blob/main/de.egwagi.Libflaps.flatpak) file, and install it using your software center.
