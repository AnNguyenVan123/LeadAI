"""What the radar is looking for. One file per product you run the pipeline for."""
from dataclasses import dataclass, field


@dataclass
class ICP:
    product: str                    # what you sell, in one paragraph
    problem: str                    # the problem your buyer feels, in THEIR words
    buyer: str                      # who signs up
    not_buyer: list[str] = field(default_factory=list)   # look-alikes that waste your time
    subreddits: list[str] = field(default_factory=list)  # seeds; expand.py adds more
    disqualifiers: list[str] = field(default_factory=list)


LEADAI = ICP(
    product=(
        "A tool that watches public online conversations (Reddit first), detects people "
        "describing a problem your product solves, scores how likely they are to buy, "
        "explains why, and drafts a reply for the founder to approve before sending."
    ),
    problem=(
        "I finished building my product and I have no idea how to find the first people "
        "who need it. I search communities by hand, open hundreds of posts, guess who might "
        "care, and lose track of everyone I talked to."
    ),
    buyer=(
        "Solo founder, indie hacker or technical founder who has already shipped something "
        "and is stuck on getting the first 10 paying customers. Does customer discovery by hand."
    ),
    not_buyer=[
        "Agencies and GTM consultants selling lead-gen services to founders",
        "People who have not built anything yet and are still looking for an idea",
        "Growth-content accounts writing 'how I got my first 100 customers' posts",
        "Enterprise sales teams that already run an SDR stack",
    ],
    subreddits=["SaaS", "startups", "indiehackers", "SideProject", "Entrepreneur",
                "EntrepreneurRideAlong", "microsaas", "B2BSaaS"],
    disqualifiers=[
        "Their own customers are offline-only (barbershops, salons, local retail) — we cannot "
        "surface those buyers from public forums, so we would be selling a promise we cannot keep",
        "Author is broke and asking for free help — do not sell, help",
    ],
)
