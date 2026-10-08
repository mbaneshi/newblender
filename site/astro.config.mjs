import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

const section = (label, fa, directory) => ({
  label,
  translations: { fa },
  collapsed: directory === "showcase",
  items: [{ autogenerate: { directory } }],
});

export default defineConfig({
  site: "https://mbaneshi.github.io",
  base: "/newblender",
  integrations: [
    starlight({
      title: "newblender",
      description: "Blender's source, redesigned for AI agents as the primary user.",
      favicon: "/favicon.svg",
      defaultLocale: "root",
      locales: {
        root: { label: "English", lang: "en" },
        fa: { label: "فارسی", lang: "fa", dir: "rtl" },
      },
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/mbaneshi/newblender" },
      ],
      editLink: { baseUrl: "https://github.com/mbaneshi/newblender/edit/dev/site/" },
      customCss: [
        "@fontsource-variable/inter",
        "@fontsource-variable/fraunces",
        "@fontsource-variable/jetbrains-mono",
        "@fontsource-variable/vazirmatn",
        "./src/styles/brand.css",
      ],
      expressiveCode: {
        themes: ["github-dark", "github-light"],
        styleOverrides: {
          codeBackground: "var(--sl-color-gray-6)",
          borderColor: "var(--sl-color-gray-5)",
          codeFontFamily: "var(--sl-font-mono)",
        },
      },
      sidebar: [
        { label: "Start here", translations: { fa: "شروع" }, items: [{ slug: "status" }] },
        section("RFCs", "سندهای طراحی", "rfc"),
        section("Discovery", "کشف", "discovery"),
        section("Live demos", "نمایش‌های زنده", "demos"),
        section("Showcase", "آثار نمونه", "showcase"),
      ],
    }),
  ],
});
