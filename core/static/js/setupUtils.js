export const setUpTooltip = () => {
	const tooltipTriggerList = document.querySelectorAll(
		'[data-bs-toggle="tooltip"]'
	);
	[...tooltipTriggerList].map(
		(tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
	);
};

export const setUpLikeDislike = () => {
	const likeDislikeTriggerList = document.querySelectorAll(
		'[data-bs-toggle="like-dislike"]'
	);
	[...likeDislikeTriggerList].map((likeDislikeTriggerEl) =>
		[...likeDislikeTriggerEl.children].forEach((btnEl) =>
			btnEl.addEventListener("click", voteSystem)
		)
	);
};

/**
 * Once a button is clicked, the vote system is triggered. This will launch a XHR request to the server.
 *
 * @param {MouseEvent} ev The element that triggers the vote.
 */
const voteSystem = (ev) => {
	const origin = window.location.origin;

	/**
	 * @type {HTMLButtonElement | HTMLElement}
	 */
	let btnEl = ev.target;

	if (btnEl.tagName.toLowerCase() != "button") {
		// We assume that text or icon was clicked instead of button
		btnEl = btnEl.parentElement;
	}

	/**
	 * @type {HTMLDivElement}
	 */
	const btnContainer = btnEl.parentElement;

	const votePositive = btnEl.getAttribute("data-bs-type") === "like";
	const [model, ID] = btnEl.getAttribute("data-bs-target").split("#");
	const voteURL = `${origin}/common/utils/vote/${model}/${ID}/?is_positive=${votePositive}`;

	btnEl.classList.remove(
		votePositive ? "btn-outline-success" : "btn-outline-danger"
	);
	btnEl.classList.add(votePositive ? "btn-success" : "btn-danger", "disabled");

	if (votePositive) {
		const btnDislike = btnContainer.querySelector('[data-bs-type="dislike"]');
		btnDislike.classList.remove("btn-danger", "disabled");
		btnDislike.classList.add("btn-outline-danger");
	} else {
		const btnLike = btnContainer.querySelector('[data-bs-type="like"]');
		btnLike.classList.remove("btn-success", "disabled");
		btnLike.classList.add("btn-outline-success");
	}

	fetch(voteURL)
		.then((response) => {
			if (response.ok) {
				return;
			}
			throw new Error(gettext("Vote failed"));
		})
		.catch((err) => {
			new Notification(err.message);
		});
};
