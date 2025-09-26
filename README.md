# Pulse Proof

A real-time smart contract vulnerability monitoring dashboard built with Next.js. Monitor your smart contracts for security vulnerabilities, view detailed proof-of-concept (PoC) code, and get instant alerts for critical issues.

## Features

- **Real-time Monitoring**: Continuous monitoring of smart contract vulnerabilities
- **Interactive PoC Viewer**: View sample proof-of-concept code for vulnerabilities in an interactive dialog
- **Priority-based Alerts**: Critical, high, medium, and low priority vulnerability classification
- **Responsive Dashboard**: Mobile-friendly interface with detailed vulnerability tables
- **Contract Management**: Add, switch between, and manage multiple contract addresses
- **Advanced Filtering**: Filter vulnerabilities by priority, category, date range, and contract hash
- **Export Capabilities**: Export vulnerability data for further analysis

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS with shadcn/ui components
- **Animations**: Framer Motion for smooth interactions
- **Icons**: Lucide React
- **TypeScript**: Full type safety throughout the application
- **Build Tool**: Turbopack for fast development builds

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, pnpm, or bun

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd pulse-proof
```

2. Install dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
# or
bun install
```

3. Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

4. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
pulse-proof/
├── app/                    # Next.js app directory
│   ├── dashboard/         # Dashboard pages
│   ├── onboarding/        # Onboarding flow
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── dashboard/         # Dashboard-specific components
│   ├── ui/               # Reusable UI components
│   └── navigation/        # Navigation components
├── lib/                   # Utility functions and services
├── types/                 # TypeScript type definitions
└── public/               # Static assets
```

## Key Components

### Vulnerability Table

- Sortable columns for all vulnerability data
- Mobile-responsive card layout
- Integrated PoC dialog viewer
- Real-time status updates

### PoC Dialog

- Interactive proof-of-concept code viewer
- Copy-to-clipboard functionality
- Sample code for different vulnerability types
- External link to full reports

### Critical Notifications

- Animated notification stack
- Real-time alerts for critical vulnerabilities
- Quick action buttons (acknowledge, dismiss)
- Expandable notification details

## Development

### Building for Production

```bash
npm run build
```

### Running Tests

```bash
npm run test
```

### Linting

```bash
npm run lint
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Icons from [Lucide](https://lucide.dev/)
- Animations powered by [Framer Motion](https://www.framer.com/motion/)
