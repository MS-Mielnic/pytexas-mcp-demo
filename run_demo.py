from agent.workflow import run_customer_strategy_workflow
from shared.demo_presenter import render_demo_output


def main():
    print("=== MCP Secure Agent Demo ===\n")
    print("Story:")
    print("- Trusted MCP server: can execute internal actions like send_email")
    print("- Untrusted MCP server: provides external enrichment data")
    print("- Agent validates untrusted data, asks for approval when needed,")
    print("  and only then may call the trusted server\n")

    customer_id = input("Enter customer_id (e.g., cust_001): ").strip()

    print("\nRunning workflow...\n")

    result = run_customer_strategy_workflow(customer_id, verbose=False)

    render_demo_output(customer_id, result)


if __name__ == "__main__":
    main()
