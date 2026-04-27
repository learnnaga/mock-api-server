{{/*
Expand the name of the chart.
*/}}
{{- define "verkada-api.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "verkada-api.fullname" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "verkada-api.labels" -}}
helm.sh/chart: {{ include "verkada-api.name" . }}-{{ .Chart.Version }}
{{ include "verkada-api.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "verkada-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "verkada-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
