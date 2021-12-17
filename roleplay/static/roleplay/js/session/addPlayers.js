const addPlayersButton = document.querySelector("#playerAddButton");
const addPlayerInput = document.querySelector("#invitePlayerInput");
const playersContainer = document.querySelector("#playersInvitedContainer");

/**
 * Adds a player to the container.
 */
const addPlayerToContainer = () => {
	if (addPlayerInput.checkValidity()) {
		const option = document.createElement("option");
		option.value = addPlayerInput.value;
		option.text = addPlayerInput.value;
		option.selected = true;
		playersContainer.append(option);
		addPlayerInput.value = "";
	}
};

document.addEventListener("DOMContentLoaded", () => {
	addPlayersButton.addEventListener("click", addPlayerToContainer);
	addPlayerInput.addEventListener("keydown", (event) => {
		if (event.key === "Enter") {
			addPlayersButton.click();
		}
	});
});
