"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import PhoneInput from "react-phone-input-2"
import "react-phone-input-2/lib/style.css"
import Select from "react-select"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { register } from "@/lib/api"
import { Eye, EyeOff } from "lucide-react"
import { COUNTRY_CURRENCY_MAP, COUNTRIES, CURRENCIES, DEVELOPER_TYPES } from "@/constants"

// Zod validation schema
const signupSchema = z
  .object({
    first_name: z.string().min(1, "First name is required").max(150, "First name is too long"),
    last_name: z.string().min(1, "Last name is required").max(150, "Last name is too long"),
    email: z.string().email("Invalid email address"),
    phone_number: z.string().min(1, "Phone number is required"),
    country: z.string().min(2, "Country is required"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
      .regex(/[a-z]/, "Password must contain at least one lowercase letter")
      .regex(/[0-9]/, "Password must contain at least one number")
      .regex(/[^A-Za-z0-9]/, "Password must contain at least one symbol"),
    confirm_password: z.string(),
    company_name: z.string().optional(),
    developer_type: z.string().optional(),
    preferred_currency: z.string().optional(),
    terms_accepted: z.boolean().refine((val) => val === true, {
      message: "You must accept the terms of service",
    }),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  })

type SignupFormData = z.infer<typeof signupSchema>

export default function SignupPage() {
  const router = useRouter()
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [detectedCountry, setDetectedCountry] = useState<string | null>(null)

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      terms_accepted: false,
    },
  })

  const selectedCountry = watch("country")
  const selectedCurrency = watch("preferred_currency")

  // Auto-detect country on mount
  useEffect(() => {
    const detectCountry = async () => {
      try {
        const response = await fetch("https://ipapi.co/json/")
        const data = await response.json()
        if (data.country_code) {
          setDetectedCountry(data.country_code)
          setValue("country", data.country_code)
          // Auto-set currency based on country
          const currency = COUNTRY_CURRENCY_MAP[data.country_code] || "USD"
          setValue("preferred_currency", currency)
        }
      } catch (err) {
        console.error("Failed to detect country:", err)
      }
    }
    detectCountry()
  }, [setValue])

  // Update currency when country changes
  useEffect(() => {
    if (selectedCountry && !selectedCurrency) {
      const currency = COUNTRY_CURRENCY_MAP[selectedCountry] || "USD"
      setValue("preferred_currency", currency)
    }
  }, [selectedCountry, selectedCurrency, setValue])

  const onSubmit = async (data: SignupFormData) => {
    setError("")
    setLoading(true)

    try {
      const response = await register({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone_number: data.phone_number,
        country: data.country,
        password: data.password,
        confirm_password: data.confirm_password,
        company_name: data.company_name || "",
        developer_type: data.developer_type || "",
        preferred_currency: data.preferred_currency || "USD",
        terms_accepted: data.terms_accepted,
      })

      if (response.error) {
        if (response.errors) {
          const errorMessages = Object.entries(response.errors)
            .map(([key, values]) => `${key}: ${Array.isArray(values) ? values.join(", ") : values}`)
            .join("\n")
          setError(errorMessages)
        } else {
          setError(response.error || "An error occurred during registration")
        }
        setLoading(false)
      } else {
        router.push("/login?message=Account created successfully. Please check your email to verify your account.")
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.")
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-card to-background px-4 py-8">
      <Card className="w-full max-w-2xl bg-card border-border">
        <CardHeader>
          <CardTitle className="text-2xl">Create Account</CardTitle>
          <CardDescription>Join PayBridge and start processing payments across Africa</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {error && (
              <div className="bg-destructive/10 border border-destructive/20 text-destructive rounded px-3 py-2 text-sm whitespace-pre-line">
                {error}
              </div>
            )}

            {/* Name Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">
                  First Name <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="first_name"
                  {...registerField("first_name")}
                  className="bg-background border-border"
                  placeholder="John"
                />
                {errors.first_name && (
                  <p className="text-sm text-destructive">{errors.first_name.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">
                  Last Name <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="last_name"
                  {...registerField("last_name")}
                  className="bg-background border-border"
                  placeholder="Doe"
                />
                {errors.last_name && (
                  <p className="text-sm text-destructive">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email">
                Email Address <span className="text-destructive">*</span>
              </Label>
              <Input
                id="email"
                type="email"
                {...registerField("email")}
                className="bg-background border-border"
                placeholder="john.doe@example.com"
              />
              {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
            </div>

            {/* Phone Number */}
            <div className="space-y-2">
              <Label htmlFor="phone_number">
                Phone Number <span className="text-destructive">*</span>
              </Label>
              <PhoneInput
                country={detectedCountry?.toLowerCase() || "us"}
                value={watch("phone_number")}
                onChange={(value) => setValue("phone_number", value)}
                inputClass="!w-full !h-9 !bg-background !border-border !rounded-md"
                buttonClass="!bg-background !border-border"
                containerClass="!w-full"
                inputProps={{
                  id: "phone_number",
                  name: "phone_number",
                }}
              />
              {errors.phone_number && (
                <p className="text-sm text-destructive">{errors.phone_number.message}</p>
              )}
            </div>

            {/* Country */}
            <div className="space-y-2">
              <Label htmlFor="country">
                Country <span className="text-destructive">*</span>
              </Label>
              <Select
                id="country"
                options={COUNTRIES}
                value={COUNTRIES.find((c) => c.value === selectedCountry) || null}
                onChange={(option) => setValue("country", option?.value || "")}
                className="react-select-container"
                classNamePrefix="react-select"
                placeholder="Select your country"
                styles={{
                  control: (base) => ({
                    ...base,
                    backgroundColor: "hsl(var(--background))",
                    borderColor: "hsl(var(--border))",
                    minHeight: "36px",
                  }),
                  menu: (base) => ({
                    ...base,
                    backgroundColor: "hsl(var(--popover))",
                  }),
                }}
              />
              {errors.country && <p className="text-sm text-destructive">{errors.country.message}</p>}
            </div>

            {/* Password Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="password">
                  Password <span className="text-destructive">*</span>
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    {...registerField("password")}
                    className="bg-background border-border pr-10"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-sm text-destructive">{errors.password.message}</p>
                )}
                {/* <p className="text-xs text-muted-foreground">
                  Must be 8+ characters with uppercase, lowercase, number, and symbol
                </p> */}
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_password">
                  Confirm Password <span className="text-destructive">*</span>
                </Label>
                <div className="relative">
                  <Input
                    id="confirm_password"
                    type={showConfirmPassword ? "text" : "password"}
                    {...registerField("confirm_password")}
                    className="bg-background border-border pr-10"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.confirm_password && (
                  <p className="text-sm text-destructive">{errors.confirm_password.message}</p>
                )}
              </div>
            </div>

            {/* Company Name */}
            <div className="space-y-2">
              <Label htmlFor="company_name">Company / Organization Name (Optional)</Label>
              <Input
                id="company_name"
                {...registerField("company_name")}
                className="bg-background border-border"
                placeholder="Acme Inc."
              />
            </div>

            {/* Developer Type */}
            <div className="space-y-2">
              <Label htmlFor="developer_type">Use Case / Developer Type</Label>
              <Select
                id="developer_type"
                options={DEVELOPER_TYPES}
                value={DEVELOPER_TYPES.find((d) => d.value === watch("developer_type")) || null}
                onChange={(option) => setValue("developer_type", option?.value || "")}
                className="react-select-container"
                classNamePrefix="react-select"
                placeholder="Select your use case"
                isClearable
                styles={{
                  control: (base) => ({
                    ...base,
                    backgroundColor: "hsl(var(--background))",
                    borderColor: "hsl(var(--border))",
                    minHeight: "36px",
                  }),
                  menu: (base) => ({
                    ...base,
                    backgroundColor: "hsl(var(--popover))",
                  }),
                }}
              />
            </div>

            {/* Preferred Currency */}
            <div className="space-y-2">
              <Label htmlFor="preferred_currency">Preferred Currency</Label>
              <Select
                id="preferred_currency"
                options={CURRENCIES}
                value={CURRENCIES.find((c) => c.value === selectedCurrency) || null}
                onChange={(option) => setValue("preferred_currency", option?.value || "USD")}
                className="react-select-container"
                classNamePrefix="react-select"
                placeholder="Select currency"
                styles={{
                  control: (base) => ({
                    ...base,
                    backgroundColor: "hsl(var(--background))",
                    borderColor: "hsl(var(--border))",
                    minHeight: "36px",
                  }),
                  menu: (base) => ({
                    ...base,
                    backgroundColor: "hsl(var(--popover))",
                  }),
                }}
              />
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-start space-x-2">
              <Checkbox
                id="terms_accepted"
                checked={watch("terms_accepted")}
                onCheckedChange={(checked) => setValue("terms_accepted", checked === true)}
                className="mt-1"
              />
              <Label htmlFor="terms_accepted" className="text-sm leading-relaxed cursor-pointer">
                I agree to the{" "}
                <Link href="/terms" className="text-primary hover:underline">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/policy" className="text-primary hover:underline">
                  Privacy Policy
                </Link>
                <span className="text-destructive">*</span>
              </Label>
            </div>
            {errors.terms_accepted && (
              <p className="text-sm text-destructive">{errors.terms_accepted.message}</p>
            )}

            <Button disabled={loading} className="w-full" type="submit">
              {loading ? "Creating account..." : "Create Account"}
            </Button>
          </form>
          <p className="text-center text-muted-foreground text-sm mt-4">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
