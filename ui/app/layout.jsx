import "./globals.css";

export const metadata = {
  title: "Eddy SAT Agent",
  description: "Digital SAT practice with an AI tutor.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
