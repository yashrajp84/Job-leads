export const metadata = {
  title: "Job Leads",
  description: "React UI for Job Leads",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial, Apple Color Emoji, Segoe UI Emoji', margin: 0 }}>
        <div style={{ padding: 16 }}>
          <h1 style={{ margin: 0 }}>Job Leads</h1>
          <div style={{ marginTop: 12 }}>{children}</div>
        </div>
      </body>
    </html>
  );
}

