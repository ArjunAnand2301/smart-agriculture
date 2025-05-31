from src.main import SmartAgricultureSystem
from datetime import datetime, timedelta

class AgriculturalAgent:
    """An agent to automate agricultural tasks and provide insights."""

    def __init__(self, monitored_fields=None):
        """Initialize the agent with a list of fields to monitor.

        Args:
            monitored_fields (list, optional): A list of field dictionaries,
                                             each with 'name' and 'coordinates'.
                                             Defaults to None.
        """
        self.system = SmartAgricultureSystem()
        self.monitored_fields = monitored_fields if monitored_fields is not None else []

    def add_field_to_monitor(self, field):
        """Add a field to the list of monitored fields.

        Args:
            field (dict): A dictionary with 'name' and 'coordinates'.
        """
        self.monitored_fields.append(field)
        print(f"Added field: {field['name']} to monitoring list.")

    def perform_scheduled_analysis(self, date=None, time_range_days=30):
        """Perform analysis for all monitored fields.

        Args:
            date (datetime.date, optional): The end date for the analysis.
                                            Defaults to today.
            time_range_days (int): The number of days prior to the end date
                                   for the analysis time range. Defaults to 30.
        """
        if not self.monitored_fields:
            print("No fields configured for monitoring.")
            return

        analysis_date = date if date is not None else datetime.now().date()
        start_date = (analysis_date - timedelta(days=time_range_days)).strftime("%Y-%m-%d")
        end_date = analysis_date.strftime("%Y-%m-%d")

        print(f"\nPerforming scheduled analysis for {len(self.monitored_fields)} fields...")
        all_results = {}
        for field in self.monitored_fields:
            print(f"Analyzing field: {field['name']} ({field['coordinates']})...")
            try:
                results = self.system.analyze_field(
                    field['coordinates'],
                    start_date,
                    end_date
                )
                all_results[field['name']] = results
                print(f"Analysis complete for {field['name']}. Results: {results.get('health_analysis', {}).get('health_score', 'N/A')}")
                # In a real agent, we would process and store these results,
                # potentially send notifications, etc.

            except Exception as e:
                print(f"Error analyzing field {field['name']}: {str(e)}")
                all_results[field['name']] = {'error': str(e)}

        return all_results # Return the collected results

    def process_analysis_results(self, results):
        """Process analysis results to generate summaries or identify anomalies.

        Args:
            results (dict): Dictionary of analysis results for each field.

        Returns:
            dict: A dictionary containing processed insights, summaries, or anomalies.
        """
        processed_insights = {}
        if not results:
            return processed_insights

        print("\nProcessing analysis results...")
        for field_name, field_results in results.items():
            summary = f"Summary for {field_name}: "
            anomalies = []

            if 'error' in field_results:
                summary += f"Analysis failed: {field_results['error']}"
                anomalies.append(f"Analysis failed for {field_name}")
            else:
                health_analysis = field_results.get('health_analysis', {})
                recommendations = field_results.get('recommendations', {})

                # Add health score to summary
                health_score = health_analysis.get('health_score', 'N/A')
                summary += f"Health Score: {health_score}. "

                # Check for low health score anomaly
                if isinstance(health_score, (int, float)) and health_score < 0.4:
                     anomalies.append(f"Low health score ({health_score:.2f}) detected for {field_name}.")

                # Add data quality status to summary and check for anomaly
                data_quality = health_analysis.get('data_quality', 'unknown')
                status_message = health_analysis.get('status_message', '')
                summary += f"Data Quality: {data_quality}. "
                if data_quality in ['limited', 'error']:
                     anomalies.append(f"Limited or error data quality for {field_name}: {status_message}")

                # Add number of recommendations to summary
                total_recommendations = sum(len(rec_list) for rec_list in recommendations.values())
                summary += f"{total_recommendations} recommendations generated."
                if total_recommendations > 5:
                     anomalies.append(f"High number of recommendations ({total_recommendations}) for {field_name}, indicating potential issues.")

                # Add key recommendations as anomalies (example)
                if recommendations.get('irrigation'):
                     anomalies.append(f"Irrigation recommendations for {field_name}.")
                if recommendations.get('pesticide'):
                     anomalies.append(f"Pesticide recommendations for {field_name}.")


            processed_insights[field_name] = {
                'summary': summary.strip(),
                'anomalies': anomalies
            }
            print(f"Processed {field_name}.")

        return processed_insights

# Example usage (for testing/demonstration)
# if __name__ == "__main__":
#     # Define some example fields
#     example_fields = [
#         {'name': 'North Field', 'coordinates': [-121.7, 38.5]},
#         {'name': 'South Field', 'coordinates': [-121.6, 38.4]},
#     ]

#     # Initialize the agent with fields
#     agent = AgriculturalAgent(monitored_fields=example_fields)

#     # Or add fields individually
#     # agent = AgriculturalAgent()
#     # agent.add_field_to_monitor({'name': 'East Field', 'coordinates': [-121.5, 38.3]})

#     # Perform analysis
#     agent.perform_scheduled_analysis() 