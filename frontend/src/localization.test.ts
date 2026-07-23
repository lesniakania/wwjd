import { describe, expect, it } from "vitest";
import { Language, copyFor } from "./localization";

describe("localization", () => {
  it("returns copy for each supported language", () => {
    expect(copyFor(Language.Polish).submit).toBe("Znajdź drogę naprzód");
    expect(copyFor(Language.English).submit).toBe("Find a way forward");
  });
});
