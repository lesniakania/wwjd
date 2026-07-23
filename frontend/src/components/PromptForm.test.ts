import { fireEvent, render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";
import PromptForm from "./PromptForm.vue";
import { Language, copyFor } from "../localization";

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
      screen.getByRole("button", { name: /find a way forward/i }),
    );

    expect(emitted().submit).toEqual([
      ["I need help responding patiently to a difficult friend."],
    ]);
  });
});
