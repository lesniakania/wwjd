import { afterEach, describe, expect, it, vi } from "vitest";
import { createShare, getShare, requestReflection } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("API client", () => {
  it("uses the localized validation message for rejected reflections", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422 }));

    await expect(requestReflection("Too short", "en")).rejects.toThrow(
      "Please describe the situation in a little more detail.",
    );
  });

  it("uses an API detail when share creation fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: "Sharing is temporarily unavailable." }),
      }),
    );

    await expect(
      createShare("A sufficiently detailed situation.", "en", {} as never),
    ).rejects.toThrow("Sharing is temporarily unavailable.");
  });

  it("encodes share identifiers", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: "a/b" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await getShare("a/b");

    expect(fetchMock).toHaveBeenCalledWith("/api/shares/a%2Fb");
  });

  it("uses the configured API base URL without duplicating slashes", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://wwjd-api.onrender.com/");
    vi.resetModules();
    const { requestReflection: requestConfiguredReflection } = await import("./api");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    });
    vi.stubGlobal("fetch", fetchMock);

    await requestConfiguredReflection("A sufficiently detailed situation.", "en");

    expect(fetchMock).toHaveBeenCalledWith(
      "https://wwjd-api.onrender.com/api/reflections",
      expect.any(Object),
    );
  });
});
