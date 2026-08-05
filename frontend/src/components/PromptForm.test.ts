import { cleanup, fireEvent, render, screen } from "@testing-library/vue";
import { afterEach, describe, expect, it } from "vitest";
import PromptForm from "./PromptForm.vue";
import { Language, copyFor } from "../localization";

afterEach(cleanup);

describe("PromptForm", () => {
  it("emits a trimmed valid situation", async () => {
    const { emitted } = render(PromptForm, {
      props: {
        copy: copyFor(Language.English),
        loading: false,
        error: "",
      },
    });

    await fireEvent.update(
      screen.getByLabelText("What would Jesus do?"),
      "  I need help responding patiently to a difficult friend.  ",
    );
    await fireEvent.click(
      screen.getByRole("button", { name: /^see$/i }),
    );

    expect(emitted().submit).toEqual([
      ["I need help responding patiently to a difficult friend."],
    ]);
  });

  it.each([
    ["Control", { ctrlKey: true }],
    ["Command", { metaKey: true }],
  ])("submits with %s+Enter", async (_modifier, keyboardOptions) => {
    const { emitted } = render(PromptForm, {
      props: {
        copy: copyFor(Language.English),
        loading: false,
        error: "",
      },
    });
    const textarea = screen.getByLabelText("What would Jesus do?");
    await fireEvent.update(
      textarea,
      "I need help responding patiently to a difficult friend.",
    );
    await fireEvent.keyDown(textarea, {
      key: "Enter",
      ctrlKey: keyboardOptions.ctrlKey === true,
      metaKey: keyboardOptions.metaKey === true,
    });

    expect(emitted().submit).toEqual([
      ["I need help responding patiently to a difficult friend."],
    ]);
  });
});
