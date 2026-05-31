{{/*
Common labels for all resources
*/}}
{{- define "miniblog.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{/*
Selector labels (dùng cho Deployment.spec.selector.matchLabels)
*/}}
{{- define "miniblog.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
PostgreSQL fullname
*/}}
{{- define "miniblog.postgresql.fullname" -}}
{{- printf "%s-%s" .Release.Name "postgresql" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Backend fullname
*/}}
{{- define "miniblog.backend.fullname" -}}
{{- printf "%s-%s" .Release.Name "backend" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Frontend fullname
*/}}
{{- define "miniblog.frontend.fullname" -}}
{{- printf "%s-%s" .Release.Name "frontend" | trunc 63 | trimSuffix "-" -}}
{{- end -}}
