import { HeroSection } from "@/components/home/HeroSection";
import { StatsSection } from "@/components/home/StatsSection";
import { HowItWorks } from "@/components/home/HowItWorks";
import { PilotProject } from "@/components/home/PilotProject";
import { ComparisonSection } from "@/components/home/ComparisonSection";
import { ComplianceSection } from "@/components/home/ComplianceSection";
import { UemoaMap } from "@/components/home/UemoaMap";
import { Footer } from "@/components/navigation/Footer";

export default function HomePage() {
  return (
    <>
      <HeroSection />
      <StatsSection />
      <HowItWorks />
      <PilotProject />
      <ComparisonSection />
      <ComplianceSection />
      <UemoaMap />
      <Footer />
    </>
  );
}
