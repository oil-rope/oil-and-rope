let addPlayersButton = document.querySelector("#playerAddButton");
let addPlayerInput = document.querySelector("#invitePlayerInput");
let playersContainer = document.querySelector("#playersInvitedContainer");

/**
 * Adds a player to the container.
 */
const addPlayerToContainer = () => {
	if (addPlayerInput.checkValidity()) {
		let option = document.createElement("option");
		option.value = addPlayerInput.value;
		option.text = addPlayerInput.value;
		option.selected = true;
		playersContainer.append(option);
		addPlayerInput.value = "";
	}
};

document.addEventListener("DOMContentLoaded", () => {
	addPlayersButton.addEventListener("click", addPlayerToContainer);
	addPlayerInput.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			addPlayerToContainer();
		}
	});
});
