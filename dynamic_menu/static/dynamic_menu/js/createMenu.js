let currentScript = document.currentScript;
let createMenuForm = currentScript.getAttribute("data-form-id");
let nameDisplayDiv = currentScript.getAttribute("data-name-container-id");
let getResolverURL = currentScript.getAttribute("data-url-resolver");
let displayURLDiv = currentScript.getAttribute(
	"data-url-resolver-container-id"
);

$(() => {
	createMenuForm = document.getElementById(createMenuForm);
	nameDisplayDiv = document.getElementById(nameDisplayDiv);
	displayURLDiv = document.getElementById(displayURLDiv);

	let prependedSelect = document.getElementById("id_prepended_text");
	let nameInput = document.getElementById("id_name");
	let appendedSelect = document.getElementById("id_appended_text");

	let urlResolverInput = document.getElementById("id_url_resolver");
	let extraURLInput = document.getElementById("id_extra_urls_args");

	/**
	 * Changes the display name of the menu.
	 */
	const changeDisplayName = () => {
		nameDisplayDiv.innerHTML = `<p class="text-center">${
			prependedSelect.value || ""
		} ${nameInput.value || ""} ${appendedSelect.value || ""}</p>`;
	};

	/**
	 * Changes the URL to display.
	 *
	 * @param {string} url
	 */
	const changeUrlDisplay = (url) => {
		displayURLDiv.innerHTML = `<p class="text-center">${url}${extraURLInput.value}</p>`;
	};

	/**
	 * Attacks the ResolverView
	 */
	const handleGetURL = () => {
		let data = { url_resolver: urlResolverInput.value };
		let headers = {
			"X-CSRFToken": Cookies.get("csrftoken"),
		};

		$.ajax({
			url: getResolverURL,
			type: "POST",
			data: data,
			headers: headers,
			success: (response) => {
				changeUrlDisplay(response.url);
			},
			error: (err) => {
				console.error(err);
			},
		});
	};

	/**
	 * Checks for changes on inputs.
	 *
	 * @param {*} e
	 */
	const handleChangeEvent = (e) => {
		let el = e.target;
		if (el === prependedSelect || el === nameInput || el === appendedSelect) {
			changeDisplayName();
		}

		if (el === urlResolverInput || el === extraURLInput) {
			handleGetURL();
		}
	};

	createMenuForm.addEventListener("change", (e) => {
		handleChangeEvent(e);
	});

	changeDisplayName();
	handleGetURL();
});
