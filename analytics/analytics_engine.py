#!/usr/bin/env python3

"""
Results Analytics Engine
Generates insights, correlations, and reports from autonomous results data
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import re
from typing import Dict, List, Any, Optional

class ResultsAnalyticsEngine:
    def __init__(self, results_root: str = "C:\\AI\\repos\\results"):
        self.results_root = Path(results_root)
        self.categories_dir = self.results_root / "categories"
        self.analytics_dir = self.results_root / "analytics"
        self.analytics_dir.mkdir(exist_ok=True)

        # Set up plotting
        plt.style.use('default')
        sns.set_palette("husl")

    def scan_results(self, category: Optional[str] = None, days: int = 30) -> Dict[str, List[Dict]]:
        """Scan and load results from specified categories"""
        results = defaultdict(list)
        cutoff_date = datetime.now() - timedelta(days=days)

        categories_to_scan = [category] if category else self.get_available_categories()

        for cat in categories_to_scan:
            cat_path = self.categories_dir / cat
            if not cat_path.exists():
                continue

            for year_dir in cat_path.glob("*/"):
                if not year_dir.is_dir():
                    continue

                for month_dir in year_dir.glob("*/"):
                    if not month_dir.is_dir():
                        continue

                    for day_dir in month_dir.glob("*/"):
                        if not day_dir.is_dir():
                            continue

                        # Check if directory is within date range
                        try:
                            dir_date = datetime(int(year_dir.name), int(month_dir.name), int(day_dir.name))
                            if dir_date < cutoff_date:
                                continue
                        except ValueError:
                            continue

                        # Load JSON files
                        for json_file in day_dir.glob("*.json"):
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    data['_file_path'] = str(json_file)
                                    data['_category'] = cat
                                    data['_date'] = dir_date
                                    results[cat].append(data)
                            except Exception as e:
                                print(f"Error loading {json_file}: {e}")

        return dict(results)

    def get_available_categories(self) -> List[str]:
        """Get list of available result categories"""
        if not self.categories_dir.exists():
            return []

        return [d.name for d in self.categories_dir.iterdir() if d.is_dir()]

    def generate_quality_report(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate quality analysis report"""
        quality_stats = {
            'overall': {'total': 0, 'avg_score': 0, 'distribution': {}},
            'by_category': {},
            'trends': [],
            'recommendations': []
        }

        all_scores = []

        for category, items in results.items():
            if not items:
                continue

            cat_scores = []
            cat_issues = Counter()

            for item in items:
                metadata = item.get('metadata', {})
                quality = metadata.get('quality', {})

                if 'score' in quality:
                    score = quality['score']
                    cat_scores.append(score)
                    all_scores.append(score)

                    # Count issues
                    for issue in quality.get('issues', []):
                        cat_issues[issue] += 1

            if cat_scores:
                quality_stats['by_category'][category] = {
                    'count': len(cat_scores),
                    'avg_score': np.mean(cat_scores),
                    'min_score': min(cat_scores),
                    'max_score': max(cat_scores),
                    'common_issues': dict(cat_issues.most_common(5))
                }

        # Overall statistics
        if all_scores:
            quality_stats['overall']['total'] = len(all_scores)
            quality_stats['overall']['avg_score'] = np.mean(all_scores)

            # Score distribution
            bins = [0, 30, 50, 70, 90, 100]
            labels = ['Poor', 'Fair', 'Good', 'Excellent']
            distribution = pd.cut(all_scores, bins=bins, labels=labels).value_counts()
            quality_stats['overall']['distribution'] = distribution.to_dict()

        # Generate recommendations
        quality_stats['recommendations'] = self._generate_quality_recommendations(quality_stats)

        return quality_stats

    def _generate_quality_recommendations(self, quality_stats: Dict) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []

        overall_avg = quality_stats['overall']['avg_score']

        if overall_avg < 50:
            recommendations.append("Critical: Overall result quality is poor. Review data sources and enrichment processes.")
        elif overall_avg < 70:
            recommendations.append("Consider improving data enrichment and quality assessment algorithms.")

        # Category-specific recommendations
        for category, stats in quality_stats['by_category'].items():
            if stats['avg_score'] < 50:
                recommendations.append(f"Category '{category}' has poor quality scores. Review ingestion pipeline.")

            # Issue-specific recommendations
            issues = stats.get('common_issues', {})
            if 'empty-data' in issues:
                recommendations.append(f"Category '{category}': Many results lack meaningful data content.")
            if 'no-timestamp' in issues:
                recommendations.append(f"Category '{category}': Add timestamp metadata to all results.")
            if 'no-source' in issues:
                recommendations.append(f"Category '{category}': Include source attribution in results.")

        return recommendations

    def analyze_correlations(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze correlations between different result types"""
        correlations = {
            'cross_category': {},
            'temporal_patterns': {},
            'content_clusters': []
        }

        # Cross-category correlations
        categories = list(results.keys())
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                correlation = self._calculate_category_correlation(
                    results[cat1], results[cat2]
                )
                if correlation > 0.3:  # Significant correlation
                    correlations['cross_category'][f"{cat1}-{cat2}"] = correlation

        # Temporal patterns
        correlations['temporal_patterns'] = self._analyze_temporal_patterns(results)

        # Content clustering
        correlations['content_clusters'] = self._cluster_similar_content(results)

        return correlations

    def _calculate_category_correlation(self, cat1_results: List[Dict], cat2_results: List[Dict]) -> float:
        """Calculate correlation between two categories based on temporal proximity"""
        if not cat1_results or not cat2_results:
            return 0.0

        # Simple correlation based on timestamp proximity
        cat1_times = [r.get('_date') for r in cat1_results if r.get('_date')]
        cat2_times = [r.get('_date') for r in cat2_results if r.get('_date')]

        if not cat1_times or not cat2_times:
            return 0.0

        # Count results within same hour
        proximity_count = 0
        total_possible = len(cat1_times) * len(cat2_times)

        for t1 in cat1_times:
            for t2 in cat2_times:
                if abs((t1 - t2).total_seconds()) < 3600:  # Within 1 hour
                    proximity_count += 1

        return proximity_count / max(total_possible, 1)

    def _analyze_temporal_patterns(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze temporal patterns in results"""
        patterns = {}

        for category, items in results.items():
            if not items:
                continue

            # Group by hour of day
            hourly_counts = Counter()
            for item in items:
                date = item.get('_date')
                if date:
                    hourly_counts[date.hour] += 1

            patterns[category] = {
                'hourly_distribution': dict(hourly_counts),
                'peak_hour': max(hourly_counts.keys(), key=lambda k: hourly_counts[k]) if hourly_counts else None,
                'total_results': len(items)
            }

        return patterns

    def _cluster_similar_content(self, results: Dict[str, List[Dict]]) -> List[Dict]:
        """Cluster results with similar content"""
        clusters = []

        # Simple clustering based on tags
        tag_groups = defaultdict(list)

        for category, items in results.items():
            for item in items:
                tags = item.get('metadata', {}).get('tags', [])
                tag_key = tuple(sorted(tags))
                if tag_key:
                    tag_groups[tag_key].append(item)

        # Convert to clusters
        for tags, items in tag_groups.items():
            if len(items) > 1:
                clusters.append({
                    'tags': list(tags),
                    'count': len(items),
                    'categories': list(set(i.get('_category') for i in items))
                })

        return sorted(clusters, key=lambda x: x['count'], reverse=True)

    def generate_insights_report(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate AI-powered insights from results"""
        insights = {
            'key_findings': [],
            'trends': [],
            'anomalies': [],
            'recommendations': [],
            'predictions': []
        }

        # Analyze quality trends
        quality_report = self.generate_quality_report(results)
        insights['key_findings'].extend(self._extract_key_findings(quality_report))

        # Analyze correlations
        correlations = self.analyze_correlations(results)
        insights['trends'].extend(self._extract_trends(correlations))

        # Detect anomalies
        insights['anomalies'].extend(self._detect_anomalies(results))

        # Generate recommendations
        insights['recommendations'].extend(self._generate_actionable_recommendations(results))

        return insights

    def _extract_key_findings(self, quality_report: Dict) -> List[str]:
        """Extract key findings from quality report"""
        findings = []

        overall_avg = quality_report['overall']['avg_score']
        if overall_avg > 85:
            findings.append(f"Excellent overall result quality ({overall_avg:.1f}%)")
        elif overall_avg > 70:
            findings.append(f"Good overall result quality ({overall_avg:.1f}%)")
        elif overall_avg > 50:
            findings.append(f"Fair overall result quality ({overall_avg:.1f}%) - room for improvement")
        else:
            findings.append(f"Poor overall result quality ({overall_avg:.1f}%) - immediate attention needed")

        # Category-specific findings
        for category, stats in quality_report['by_category'].items():
            if stats['avg_score'] > 90:
                findings.append(f"Category '{category}' shows exceptional quality")
            elif stats['avg_score'] < 50:
                findings.append(f"Category '{category}' requires quality improvement")

        return findings

    def _extract_trends(self, correlations: Dict) -> List[str]:
        """Extract trends from correlation analysis"""
        trends = []

        # Cross-category correlations
        for pair, correlation in correlations['cross_category'].items():
            if correlation > 0.7:
                trends.append(f"Strong correlation between {pair} categories")
            elif correlation > 0.5:
                trends.append(f"Moderate correlation between {pair} categories")

        # Temporal patterns
        for category, pattern in correlations['temporal_patterns'].items():
            peak_hour = pattern.get('peak_hour')
            if peak_hour is not None:
                trends.append(f"Category '{category}' peaks at hour {peak_hour}")

        return trends

    def _detect_anomalies(self, results: Dict[str, List[Dict]]) -> List[str]:
        """Detect anomalies in results"""
        anomalies = []

        for category, items in results.items():
            if not items:
                continue

            # Check for unusual quality scores
            scores = [i.get('metadata', {}).get('quality', {}).get('score', 0) for i in items]
            if scores:
                mean_score = np.mean(scores)
                std_score = np.std(scores)

                outliers = [s for s in scores if abs(s - mean_score) > 2 * std_score]
                if outliers:
                    anomalies.append(f"Category '{category}' has {len(outliers)} quality score outliers")

            # Check for unusual volumes
            if len(items) > 1000:
                anomalies.append(f"Category '{category}' has unusually high volume ({len(items)} results)")

        return anomalies

    def _generate_actionable_recommendations(self, results: Dict[str, List[Dict]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Volume-based recommendations
        total_results = sum(len(items) for items in results.values())
        if total_results > 10000:
            recommendations.append("Consider implementing result archiving for high-volume categories")

        # Category-specific recommendations
        for category, items in results.items():
            if len(items) == 0:
                recommendations.append(f"No results found for category '{category}' - check ingestion pipeline")
            elif len(items) < 10:
                recommendations.append(f"Low result volume for category '{category}' - verify data sources")

        # Quality-based recommendations
        quality_report = self.generate_quality_report(results)
        recommendations.extend(quality_report.get('recommendations', []))

        return recommendations

    def create_visualizations(self, results: Dict[str, List[Dict]]) -> str:
        """Create visualizations and return report path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.analytics_dir / f"report_{timestamp}"
        report_dir.mkdir(exist_ok=True)

        # Quality distribution chart
        self._create_quality_chart(results, report_dir)

        # Category volume chart
        self._create_volume_chart(results, report_dir)

        # Temporal patterns chart
        self._create_temporal_chart(results, report_dir)

        # Generate HTML report
        html_path = self._generate_html_report(results, report_dir, timestamp)

        return str(html_path)

    def _create_quality_chart(self, results: Dict[str, List[Dict]], report_dir: Path):
        """Create quality distribution chart"""
        quality_data = []

        for category, items in results.items():
            for item in items:
                score = item.get('metadata', {}).get('quality', {}).get('score', 0)
                quality_data.append({'category': category, 'score': score})

        if quality_data:
            df = pd.DataFrame(quality_data)

            plt.figure(figsize=(12, 6))
            sns.boxplot(data=df, x='category', y='score')
            plt.title('Result Quality Distribution by Category')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(report_dir / 'quality_distribution.png', dpi=150, bbox_inches='tight')
            plt.close()

    def _create_volume_chart(self, results: Dict[str, List[Dict]], report_dir: Path):
        """Create category volume chart"""
        volumes = {cat: len(items) for cat, items in results.items()}

        if volumes:
            plt.figure(figsize=(10, 6))
            plt.bar(volumes.keys(), volumes.values())
            plt.title('Results Volume by Category')
            plt.xticks(rotation=45)
            plt.ylabel('Number of Results')
            plt.tight_layout()
            plt.savefig(report_dir / 'category_volumes.png', dpi=150, bbox_inches='tight')
            plt.close()

    def _create_temporal_chart(self, results: Dict[str, List[Dict]], report_dir: Path):
        """Create temporal patterns chart"""
        temporal_data = []

        for category, items in results.items():
            hourly_counts = Counter()
            for item in items:
                date = item.get('_date')
                if date:
                    hourly_counts[date.hour] += 1

            for hour, count in hourly_counts.items():
                temporal_data.append({'category': category, 'hour': hour, 'count': count})

        if temporal_data:
            df = pd.DataFrame(temporal_data)

            plt.figure(figsize=(12, 6))
            sns.lineplot(data=df, x='hour', y='count', hue='category')
            plt.title('Temporal Distribution by Category')
            plt.xlabel('Hour of Day')
            plt.ylabel('Result Count')
            plt.tight_layout()
            plt.savefig(report_dir / 'temporal_patterns.png', dpi=150, bbox_inches='tight')
            plt.close()

    def _generate_html_report(self, results: Dict[str, List[Dict]], report_dir: Path, timestamp: str) -> Path:
        """Generate comprehensive HTML report"""
        quality_report = self.generate_quality_report(results)
        correlations = self.analyze_correlations(results)
        insights = self.generate_insights_report(results)

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Results Analytics Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .metric {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .chart {{ margin: 20px 0; text-align: center; }}
        .insights {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .warning {{ background: #f8d7da; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .success {{ background: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Autonomous Results Analytics Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total Results:</strong> {sum(len(items) for items in results.values())}</p>
        <p><strong>Categories:</strong> {', '.join(results.keys())}</p>
    </div>

    <div class="section">
        <h2>📊 Quality Overview</h2>
        <div class="metric">
            <h3>Overall Quality Score: {quality_report['overall']['avg_score']:.1f}%</h3>
            <p>Distribution: {', '.join(f'{k}: {v}' for k, v in quality_report['overall']['distribution'].items())}</p>
        </div>

        <h3>Quality by Category</h3>
        <table>
            <tr><th>Category</th><th>Count</th><th>Avg Score</th><th>Min Score</th><th>Max Score</th></tr>
            {"".join(f"<tr><td>{cat}</td><td>{stats['count']}</td><td>{stats['avg_score']:.1f}</td><td>{stats['min_score']}</td><td>{stats['max_score']}</td></tr>" for cat, stats in quality_report['by_category'].items())}
        </table>
    </div>

    <div class="section">
        <h2>🔍 Key Insights</h2>
        {"".join(f'<div class="insights">💡 {insight}</div>' for insight in insights['key_findings'])}

        <h3>Trends</h3>
        {"".join(f'<div class="insights">📈 {trend}</div>' for trend in insights['trends'])}

        <h3>Anomalies</h3>
        {"".join(f'<div class="warning">⚠️ {anomaly}</div>' for anomaly in insights['anomalies'])}

        <h3>Recommendations</h3>
        {"".join(f'<div class="success">✅ {rec}</div>' for rec in insights['recommendations'])}
    </div>

    <div class="section">
        <h2>📈 Visualizations</h2>
        <div class="chart">
            <img src="quality_distribution.png" alt="Quality Distribution" style="max-width: 100%;">
        </div>
        <div class="chart">
            <img src="category_volumes.png" alt="Category Volumes" style="max-width: 100%;">
        </div>
        <div class="chart">
            <img src="temporal_patterns.png" alt="Temporal Patterns" style="max-width: 100%;">
        </div>
    </div>

    <div class="section">
        <h2>🔗 Cross-Category Correlations</h2>
        <ul>
        {"".join(f"<li><strong>{pair}:</strong> {corr:.2f}</li>" for pair, corr in correlations['cross_category'].items())}
        </ul>
    </div>
</body>
</html>
"""

        html_path = report_dir / 'analytics_report.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return html_path

    def run_full_analysis(self, days: int = 30) -> str:
        """Run complete analytics pipeline"""
        print("🔍 Scanning results...")
        results = self.scan_results(days=days)

        print("📊 Generating analytics report...")
        report_path = self.create_visualizations(results)

        print(f"✅ Analytics report generated: {report_path}")
        return report_path

if __name__ == "__main__":
    engine = ResultsAnalyticsEngine()
    report_path = engine.run_full_analysis()
    print(f"📄 Open report: {report_path}")