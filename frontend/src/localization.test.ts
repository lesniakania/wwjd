import { describe, expect, it } from "vitest";
import { Language, copyFor } from "./localization";

describe("localization", () => {
  it("returns copy for each supported language", () => {
    expect(copyFor(Language.Polish).eyebrow).toBe("Hm, a ciekawe");
    expect(copyFor(Language.Polish).intro).toBe(
      "Napisz, co Cię martwi. Poszukamy pomocnych fragmentów Biblii i podpowiemy, jak możesz spojrzeć na tę sytuację.",
    );
    expect(copyFor(Language.English).intro).toBe(
      "Tell us what’s worrying you. We’ll find helpful Bible passages and suggest a way to look at the situation.",
    );
    expect(copyFor(Language.Polish).submit).toBe("Zobacz");
    expect(copyFor(Language.Polish).contextSources).toBe(
      "Kontekst na podstawie tych źródeł",
    );
    expect(copyFor(Language.English).eyebrow).toBe("Hmm, interesting");
    expect(copyFor(Language.English).submit).toBe("See");
  });

  it("provides the complete algorithm explanation in both languages", () => {
    for (const language of [Language.Polish, Language.English]) {
      const copy = copyFor(language);
      expect(copy.algorithmSteps).toHaveLength(6);
      expect(copy.algorithmTitle).toBeTruthy();
      expect(copy.algorithmIntro).toBeTruthy();
      expect(copy.algorithmSafeguard).toBeTruthy();
    }
  });
});
