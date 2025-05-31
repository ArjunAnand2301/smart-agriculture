import folium
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json
from pathlib import Path

class Visualizer:
    def __init__(self):
        """Initialize the Visualizer."""
        self.output_dir = Path('output/visualizations')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_analysis_visualization(self, imagery_data, health_analysis, recommendations):
        """
        Create comprehensive visualization of analysis results.
        
        Args:
            imagery_data (dict): Satellite imagery data
            health_analysis (dict): Health analysis results
            recommendations (dict): Resource optimization recommendations
        """
        try:
            # Create timestamp for unique filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Generate different types of visualizations
            self._create_health_map(imagery_data, health_analysis, timestamp)
            self._create_health_trends(health_analysis, timestamp)
            self._create_recommendations_chart(recommendations, timestamp)
            
            # Create an HTML report combining all visualizations
            self._create_html_report(imagery_data, health_analysis, recommendations, timestamp)
            
        except Exception as e:
            print(f"Error creating visualizations: {str(e)}")
            raise

    def _create_health_map(self, imagery_data, health_analysis, timestamp):
        """Create an interactive map showing crop health."""
        try:
            # Create a base map centered on the field
            center_lat = imagery_data.get('metadata', {}).get('center_lat', 0)
            center_lon = imagery_data.get('metadata', {}).get('center_lon', 0)
            
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=15,
                tiles='OpenStreetMap'
            )
            
            # Add health layer
            health_score = health_analysis.get('health_score', 0.5)
            color = self._get_health_color(health_score)
            
            folium.Circle(
                location=[center_lat, center_lon],
                radius=500,
                color=color,
                fill=True,
                popup=f"Health Score: {health_score:.2f}"
            ).add_to(m)
            
            # Add satellite imagery layer if available
            if 'image_url' in imagery_data.get('metadata', {}):
                folium.raster_layers.ImageOverlay(
                    imagery_data['metadata']['image_url'],
                    bounds=[[center_lat-0.01, center_lon-0.01],
                           [center_lat+0.01, center_lon+0.01]],
                    opacity=0.7
                ).add_to(m)
            
            # Save the map
            map_path = self.output_dir / f'health_map_{timestamp}.html'
            m.save(str(map_path))
            
        except Exception as e:
            print(f"Error creating health map: {str(e)}")
            raise

    def _create_health_trends(self, health_analysis, timestamp):
        """Create health trend visualization."""
        try:
            # Create a figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Plot health score
            health_score = health_analysis.get('health_score', 0.5)
            ax1.bar(['Health Score'], [health_score], color=self._get_health_color(health_score))
            ax1.set_ylim(0, 1)
            ax1.set_title('Crop Health Score')
            
            # Plot detailed metrics if available
            if 'detailed_metrics' in health_analysis:
                metrics = health_analysis['detailed_metrics']
                labels = list(metrics.keys())
                values = list(metrics.values())
                
                ax2.bar(labels, values, color='skyblue')
                ax2.set_ylim(0, 1)
                ax2.set_title('Detailed Health Metrics')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Save the plot
            plot_path = self.output_dir / f'health_trends_{timestamp}.png'
            plt.savefig(plot_path)
            plt.close()
            
        except Exception as e:
            print(f"Error creating health trends: {str(e)}")
            raise

    def _create_recommendations_chart(self, recommendations, timestamp):
        """Create visualization of recommendations."""
        try:
            # Create a figure
            plt.figure(figsize=(12, 6))
            
            # Extract recommendation categories and counts
            categories = list(recommendations.keys())
            counts = [len(recommendations[cat]) for cat in categories]
            
            # Create bar chart
            plt.bar(categories, counts, color='lightgreen')
            plt.title('Recommendation Categories')
            plt.xticks(rotation=45)
            plt.ylabel('Number of Recommendations')
            
            plt.tight_layout()
            
            # Save the plot
            plot_path = self.output_dir / f'recommendations_{timestamp}.png'
            plt.savefig(plot_path)
            plt.close()
            
        except Exception as e:
            print(f"Error creating recommendations chart: {str(e)}")
            raise

    def _create_html_report(self, imagery_data, health_analysis, recommendations, timestamp):
        """Create an HTML report combining all visualizations."""
        try:
            report_path = self.output_dir / f'analysis_report_{timestamp}.html'
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Smart Agriculture Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .section {{ margin-bottom: 30px; }}
                    .visualization {{ margin: 20px 0; }}
                    h1, h2 {{ color: #2c3e50; }}
                    .recommendation {{ background-color: #f8f9fa; padding: 10px; margin: 5px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Smart Agriculture Analysis Report</h1>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <div class="section">
                        <h2>Crop Health Analysis</h2>
                        <p>Health Score: {health_analysis.get('health_score', 0):.2f}</p>
                        <p>Status: {health_analysis.get('health_status', 'Unknown')}</p>
                        <div class="visualization">
                            <iframe src="health_map_{timestamp}.html" width="100%" height="500px" frameborder="0"></iframe>
                        </div>
                        <div class="visualization">
                            <img src="health_trends_{timestamp}.png" alt="Health Trends" style="max-width: 100%;">
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Recommendations</h2>
                        <div class="visualization">
                            <img src="recommendations_{timestamp}.png" alt="Recommendations" style="max-width: 100%;">
                        </div>
                        <h3>Detailed Recommendations:</h3>
                        {self._format_recommendations_html(recommendations)}
                    </div>
                </div>
            </body>
            </html>
            """
            
            with open(report_path, 'w') as f:
                f.write(html_content)
            
        except Exception as e:
            print(f"Error creating HTML report: {str(e)}")
            raise

    def _get_health_color(self, health_score):
        """Get color based on health score."""
        if health_score >= 0.8:
            return 'green'
        elif health_score >= 0.6:
            return 'lightgreen'
        elif health_score >= 0.4:
            return 'orange'
        else:
            return 'red'

    def _format_recommendations_html(self, recommendations):
        """Format recommendations as HTML."""
        html = ""
        for category, recs in recommendations.items():
            html += f"<h4>{category.replace('_', ' ').title()}</h4>"
            if isinstance(recs, dict):
                for key, value in recs.items():
                    html += f"<div class='recommendation'><strong>{key}:</strong> {value}</div>"
            elif isinstance(recs, list):
                for rec in recs:
                    html += f"<div class='recommendation'>{rec}</div>"
            else:
                html += f"<div class='recommendation'>{recs}</div>"
        return html 