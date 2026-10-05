document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(
        "div.highlight-bash, div.highlight-python"
    ).forEach(function (block) {

        const container = block.parentElement;

        if (container.classList.contains("code-block-wrapper")) {
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "code-block-wrapper";

        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);

        const language = block.classList.contains("highlight-python")
            ? "python"
            : "bash";

        const label = document.createElement("span");
        label.className = "code-language";
        label.textContent = language;

        const button = document.createElement("button");
        button.className = "copy-code";
        button.textContent = "📋";
        button.title = "Copy code";

        button.addEventListener("click", function () {
            const code = block.querySelector("code");

            navigator.clipboard.writeText(code.innerText).then(function () {
                button.textContent = "✓";

                setTimeout(function () {
                    button.textContent = "📋";
                }, 1500);
            });
        });

        wrapper.appendChild(label);
        wrapper.appendChild(button);
    });
});