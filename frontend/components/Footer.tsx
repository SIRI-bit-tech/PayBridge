import Link from "next/link"
import { Facebook, Twitter, Linkedin, Instagram, Github, Heart } from "lucide-react"

const footerLinks = {
  product: [
    { name: "Features", href: "/#features" },
    { name: "Pricing", href: "/pricing" },
    { name: "API", href: "/developers" },
    { name: "Integrations", href: "/integrations" },
  ],
  company: [
    { name: "About Us", href: "/about" },
    { name: "Careers", href: "/careers" },
    { name: "Blog", href: "/blog" },
    { name: "Press", href: "/press" },
  ],
  resources: [
    { name: "Documentation", href: "/docs" },
    { name: "Guides", href: "/guides" },
    { name: "Help Center", href: "/help" },
    { name: "Community", href: "/community" },
  ],
  legal: [
    { name: "Privacy Policy", href: "/policy" },
    { name: "Terms of Service", href: "/terms" },
    { name: "Cookie Policy", href: "/cookie-policy" },
    { name: "GDPR", href: "/gdpr" },
  ],
  social: [
    {
      name: 'Facebook',
      href: '#',
      icon: Facebook,
    },
    {
      name: 'Instagram',
      href: '#',
      icon: Instagram,
    },
    {
      name: 'Twitter',
      href: '#',
      icon: Twitter,
    },
    {
      name: 'GitHub',
      href: '#',
      icon: Github,
    },
    {
      name: 'LinkedIn',
      href: '#',
      icon: Linkedin,
    },
  ],
}

export function Footer() {
  return (
    <footer className="bg-sidebar border-t border-sidebar-border" aria-labelledby="footer-heading">
      <h2 id="footer-heading" className="sr-only">Footer</h2>
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8">
        <div className="xl:grid xl:grid-cols-3 xl:gap-8">
          <div className="space-y-8 xl:col-span-1">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-sidebar-foreground">PayBridge</span>
            </div>
            <p className="text-muted-foreground text-base">
              Empowering businesses with seamless payment solutions across Africa.
            </p>
            <div className="flex space-x-6">
              {footerLinks.social.map((item) => (
                <Link key={item.name} href={item.href} className="text-muted-foreground hover:text-primary transition-colors">
                  <span className="sr-only">{item.name}</span>
                  <item.icon className="h-6 w-6" aria-hidden="true" />
                </Link>
              ))}
            </div>
          </div>
          <div className="mt-12 grid grid-cols-2 gap-8 xl:mt-0 xl:col-span-2">
            <div className="md:grid md:grid-cols-2 md:gap-8">
              <div>
                <h3 className="text-sm font-semibold text-sidebar-foreground tracking-wider uppercase">Product</h3>
                <ul role="list" className="mt-4 space-y-4">
                  {footerLinks.product.map((item) => (
                    <li key={item.name}>
                      <Link href={item.href} className="text-base text-muted-foreground hover:text-primary transition-colors">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="mt-12 md:mt-0">
                <h3 className="text-sm font-semibold text-sidebar-foreground tracking-wider uppercase">Company</h3>
                <ul role="list" className="mt-4 space-y-4">
                  {footerLinks.company.map((item) => (
                    <li key={item.name}>
                      <Link href={item.href} className="text-base text-muted-foreground hover:text-primary transition-colors">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="md:grid md:grid-cols-2 md:gap-8">
              <div>
                <h3 className="text-sm font-semibold text-sidebar-foreground tracking-wider uppercase">Resources</h3>
                <ul role="list" className="mt-4 space-y-4">
                  {footerLinks.resources.map((item) => (
                    <li key={item.name}>
                      <Link href={item.href} className="text-base text-muted-foreground hover:text-primary transition-colors">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="mt-12 md:mt-0">
                <h3 className="text-sm font-semibold text-sidebar-foreground tracking-wider uppercase">Legal</h3>
                <ul role="list" className="mt-4 space-y-4">
                  {footerLinks.legal.map((item) => (
                    <li key={item.name}>
                      <Link href={item.href} className="text-base text-muted-foreground hover:text-primary transition-colors">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-12 border-t border-sidebar-border pt-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex space-x-6 md:order-2">
              {footerLinks.social.map((item) => (
                <Link key={item.name} href={item.href} className="text-muted-foreground hover:text-primary transition-colors">
                  <span className="sr-only">{item.name}</span>
                  <item.icon className="h-6 w-6" aria-hidden="true" />
                </Link>
              ))}
            </div>
            <p className="mt-8 text-base text-muted-foreground md:mt-0 md:order-1">
              &copy; {new Date().getFullYear()} PayBridge, Inc. All rights reserved.
            </p>
          </div>
          <div className="mt-8 md:mt-0">
            <p className="text-xs text-muted-foreground opacity-80">
              PayBridge is a registered trademark of PayBridge, Inc. All other trademarks are the property of their respective owners.
            </p>
            <p className="mt-2 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1">
                Made with <Heart className="h-3 w-3 text-red-500" aria-hidden="true" /> in Africa for the world.
              </span>
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}