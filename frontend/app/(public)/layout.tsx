import { Footer } from "@/components/Footer"

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen relative bg-background text-foreground">
      {/* background decorations */}
      <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 right-[-10%] h-[38rem] w-[38rem] rounded-full bg-primary/20 blur-3xl" />
        <div className="absolute -bottom-40 left-[-10%] h-[32rem] w-[32rem] rounded-full bg-accent/10 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(23,77,56,0.08),transparent_50%)]" />
      </div>

      <div className="relative z-10">{children}</div>

      <Footer />
    </div>
  )
}