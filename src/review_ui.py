
import streamlit as st


def render_review(findings, condition, session_id, log_event, save_decision):
    progressive = condition == "Progressive disclosure"

    st.subheader("AI-generated review findings")

    st.caption(
        "Summaries appear first; inspect findings for more detail."
        if progressive
        else "All finding details are displayed together."
    )

    for finding in findings:
        finding_id = finding["id"]

        with st.container(border=True):
            left, right = st.columns([4, 1])

            left.markdown(f"**{finding_id} · {finding['title']}**")
            right.markdown(f"**{finding['severity']}**")

            st.write(finding["summary"])

            if progressive:
                details_key = f"details_open_{session_id}_{finding_id}"

                if details_key not in st.session_state:
                    st.session_state[details_key] = False

                button_label = (
                    "Hide details"
                    if st.session_state[details_key]
                    else "Inspect explanation, evidence and suggestion"
                )

                if st.button(
                    button_label,
                    key=f"inspect_{session_id}_{finding_id}"
                ):
                    if not st.session_state[details_key]:
                        log_event(
                            session_id,
                            "finding_expanded",
                            {"finding_id": finding_id}
                        )

                    st.session_state[details_key] = (
                        not st.session_state[details_key]
                    )

                if st.session_state[details_key]:
                    st.markdown("**Explanation**")
                    st.write(finding["explanation"])

                    st.markdown("**Evidence**")
                    st.write(finding["evidence"])

                    st.markdown("**Suggested action**")
                    st.write(finding["suggestion"])

            else:
                st.markdown("**Explanation**")
                st.write(finding["explanation"])

                st.markdown("**Evidence**")
                st.write(finding["evidence"])

                st.markdown("**Suggested action**")
                st.write(finding["suggestion"])

            choice = st.radio(
                "Your assessment",
                ["Accept finding", "Reject finding", "Unsure"],
                key=f"decision_{session_id}_{finding_id}",
                index=None,
                horizontal=True
            )

            comment = st.text_input(
                "Optional comment",
                key=f"comment_{session_id}_{finding_id}"
            )

            if st.button(
                "Save assessment",
                key=f"save_{session_id}_{finding_id}"
            ):
                if choice is None:
                    st.warning("Choose an assessment first.")
                else:
                    save_decision(
                        session_id,
                        finding_id,
                        choice,
                        comment
                    )

                    log_event(
                        session_id,
                        "finding_decision_saved",
                        {
                            "finding_id": finding_id,
                            "decision": choice
                        }
                    )

                    st.success("Assessment saved.")
