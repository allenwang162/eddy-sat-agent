import "./globals.css";

export const metadata = {
  title: "Eddy SAT GOAT",
  description: "Digital SAT practice with an AI tutor.",
  icons: {
    icon: "/assets/favicon.png",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
