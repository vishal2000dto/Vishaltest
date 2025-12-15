#!/usr/bin/env python3
"""
Script to analyze ServiceNow catalog items and their compatibility with the
create_service_catalog_form_card function.

This script:
1. Loads the catalog_data.json file
2. Analyzes field types present in variables
3. Compares with supported types in create_service_catalog_form_card
4. Reports statistics on compatibility and potential rendering issues
"""

import json
import os
import sys
from collections import Counter, defaultdict

# Path to the JSON data file
JSON_FILE = "scripts/output/catalog_data.json"

# Field types supported by create_service_catalog_form_card function
SUPPORTED_FIELD_TYPES = [
    "Single Line Text",
    "Multi Line Text",
    "Date",
    "Select Box",
    "Multiple Choice",
    "Lookup Select Box",
    "Reference",
    "List Collector",
]

# Container and structural field types that don't need direct UI components
CONTAINER_FIELD_TYPES = [
    "Container Start",
    "Container End",
    "Macro",  # Macro fields are usually rendered server-side
    "24",  # Appears to be some kind of spacer or formatter
    "32",  # Appears to be some kind of spacer or formatter
    "33",  # Appears to be some kind of file/attachment handler
]


def analyze_catalog_compatibility():
    """Analyze catalog data compatibility with form card generator."""

    # Load the JSON data
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        sys.exit(1)

    print("=== ServiceNow Catalog Form Compatibility Analysis ===\n")

    # Get basic statistics
    catalogs = data.get("catalogs", [])
    variables = data.get("variables", [])

    print(f"Total catalog items: {len(catalogs)}")
    print(f"Total form variables: {len(variables)}")

    # Find unique catalog items with variables
    catalog_ids_with_vars = set(
        v.get("catalog_sys_id", "") for v in variables if v.get("catalog_sys_id")
    )
    print(
        f"Catalog items with variables: {len(catalog_ids_with_vars)} of {len(catalogs)} ({len(catalog_ids_with_vars)/len(catalogs)*100:.1f}%)\n"
    )

    # Analyze field types
    all_field_types = set()
    unsupported_field_types = set()

    for var in variables:
        field_type = var.get("field", {}).get("type", "")
        if field_type:
            all_field_types.add(field_type)
            if (
                field_type not in SUPPORTED_FIELD_TYPES
                and field_type not in CONTAINER_FIELD_TYPES
            ):
                unsupported_field_types.add(field_type)

    print(f"All field types ({len(all_field_types)}):")
    print(", ".join(sorted(all_field_types)))
    print()

    print(
        f"Supported types in create_service_catalog_form_card ({len(SUPPORTED_FIELD_TYPES)}):"
    )
    print(", ".join(sorted(SUPPORTED_FIELD_TYPES)))
    print()

    print(
        f"Container/structural types (handled implicitly) ({len(CONTAINER_FIELD_TYPES)}):"
    )
    print(", ".join(sorted(CONTAINER_FIELD_TYPES)))
    print()

    print(f"Unsupported types ({len(unsupported_field_types)}):")
    print(", ".join(sorted(unsupported_field_types)))
    print()

    # Analyze catalogs with variables by field type compatibility
    catalog_var_counts = defaultdict(int)
    catalog_unsupported_counts = defaultdict(int)
    catalog_field_types = defaultdict(set)
    catalog_unsupported_types = defaultdict(set)

    for var in variables:
        catalog_id = var.get("catalog_sys_id", "")
        if not catalog_id:
            continue

        field_type = var.get("field", {}).get("type", "")
        if field_type:
            catalog_var_counts[catalog_id] += 1
            catalog_field_types[catalog_id].add(field_type)

            if (
                field_type not in SUPPORTED_FIELD_TYPES
                and field_type not in CONTAINER_FIELD_TYPES
            ):
                catalog_unsupported_counts[catalog_id] += 1
                catalog_unsupported_types[catalog_id].add(field_type)

    # Calculate compatibility metrics
    fully_compatible = 0
    partially_compatible = 0
    problematic = 0

    catalog_compatibility = {}
    for catalog_id in catalog_ids_with_vars:
        total_vars = catalog_var_counts[catalog_id]
        unsupported_vars = catalog_unsupported_counts[catalog_id]

        if unsupported_vars == 0:
            compatibility = "Fully Compatible"
            fully_compatible += 1
        elif unsupported_vars / total_vars < 0.2:  # Less than 20% unsupported
            compatibility = "Partially Compatible"
            partially_compatible += 1
        else:
            compatibility = "Problematic"
            problematic += 1

        catalog_compatibility[catalog_id] = {
            "compatibility": compatibility,
            "total_vars": total_vars,
            "unsupported_vars": unsupported_vars,
            "unsupported_types": list(catalog_unsupported_types[catalog_id]),
        }

    # Print compatibility summary
    print("=== Compatibility Summary ===")
    print(
        f"Fully Compatible: {fully_compatible} ({fully_compatible/len(catalog_ids_with_vars)*100:.1f}%)"
    )
    print(
        f"Partially Compatible: {partially_compatible} ({partially_compatible/len(catalog_ids_with_vars)*100:.1f}%)"
    )
    print(
        f"Problematic: {problematic} ({problematic/len(catalog_ids_with_vars)*100:.1f}%)"
    )
    print()

    # List problematic catalogs
    if problematic > 0:
        print("=== Top Problematic Catalogs ===")
        problematic_catalogs = [
            (cid, catalog_compatibility[cid])
            for cid in catalog_ids_with_vars
            if catalog_compatibility[cid]["compatibility"] == "Problematic"
        ]

        # Sort by percentage of unsupported variables (highest first)
        problematic_catalogs.sort(
            key=lambda x: x[1]["unsupported_vars"] / x[1]["total_vars"], reverse=True
        )

        # Get catalog names
        catalog_names = {c.get("sys_id", ""): c.get("name", "") for c in catalogs}

        for i, (catalog_id, details) in enumerate(
            problematic_catalogs[:10]
        ):  # Show top 10
            name = catalog_names.get(catalog_id, "Unknown")
            pct_unsupported = details["unsupported_vars"] / details["total_vars"] * 100
            print(f"{i+1}. {name} (ID: {catalog_id}):")
            print(
                f"   - {details['unsupported_vars']} of {details['total_vars']} variables unsupported ({pct_unsupported:.1f}%)"
            )
            print(f"   - Unsupported types: {', '.join(details['unsupported_types'])}")
            print()

    # Analyze field type frequencies
    field_type_counter = Counter()
    for var in variables:
        field_type = var.get("field", {}).get("type", "")
        if field_type:
            field_type_counter[field_type] += 1

    print("=== Field Type Frequencies ===")
    total_fields = sum(field_type_counter.values())
    for field_type, count in field_type_counter.most_common():
        status = (
            "✅ Supported"
            if field_type in SUPPORTED_FIELD_TYPES
            else (
                "⚙️ Container"
                if field_type in CONTAINER_FIELD_TYPES
                else "❌ Unsupported"
            )
        )
        print(f"{field_type}: {count} ({count/total_fields*100:.1f}%) - {status}")

    # Calculate overall compatibility percentage
    supported_count = sum(field_type_counter[ft] for ft in SUPPORTED_FIELD_TYPES)
    container_count = sum(field_type_counter[ft] for ft in CONTAINER_FIELD_TYPES)
    unsupported_count = total_fields - supported_count - container_count

    print("\n=== Overall Compatibility ===")
    print(
        f"Directly Supported: {supported_count} of {total_fields} ({supported_count/total_fields*100:.1f}%)"
    )
    print(
        f"Container/Structural: {container_count} of {total_fields} ({container_count/total_fields*100:.1f}%)"
    )
    print(
        f"Unsupported: {unsupported_count} of {total_fields} ({unsupported_count/total_fields*100:.1f}%)"
    )

    # Save detailed results to file
    output_dir = "scripts/analysis_output"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/catalog_compatibility.json", "w") as f:
        json.dump(
            {
                "summary": {
                    "total_catalogs": len(catalogs),
                    "catalogs_with_variables": len(catalog_ids_with_vars),
                    "fully_compatible": fully_compatible,
                    "partially_compatible": partially_compatible,
                    "problematic": problematic,
                    "supported_fields": supported_count,
                    "container_fields": container_count,
                    "unsupported_fields": unsupported_count,
                    "total_fields": total_fields,
                },
                "field_types": {
                    "all": list(sorted(all_field_types)),
                    "supported": SUPPORTED_FIELD_TYPES,
                    "container": CONTAINER_FIELD_TYPES,
                    "unsupported": list(sorted(unsupported_field_types)),
                },
                "field_frequencies": {
                    k: v for k, v in field_type_counter.most_common()
                },
                "catalog_compatibility": catalog_compatibility,
            },
            f,
            indent=2,
        )

    print(f"\nDetailed results saved to {output_dir}/catalog_compatibility.json")


if __name__ == "__main__":
    analyze_catalog_compatibility()
