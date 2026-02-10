#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="/home/k8s-home-lab/platform/exports"

namespaces=(awx default drone grafana kube-node-lease kube-public kube-system kubernetes-dashboard local-path-storage longhorn-system metallb-system monitoring traefik websites)

# Cluster-scoped resources
kubectl get namespace -o yaml > "${OUT_DIR}/_cluster/namespaces.yaml"
kubectl get crd -o yaml > "${OUT_DIR}/_cluster/crds.yaml"
kubectl get clusterrole -o yaml > "${OUT_DIR}/_cluster/clusterroles.yaml"
kubectl get clusterrolebinding -o yaml > "${OUT_DIR}/_cluster/clusterrolebindings.yaml"
kubectl get storageclass -o yaml > "${OUT_DIR}/_cluster/storageclasses.yaml"

for ns in "${namespaces[@]}"; do
  ns_dir="${OUT_DIR}/${ns}"
  mkdir -p "${ns_dir}"
  # Core and common resources (exclude secrets)
  kubectl -n "${ns}" get all -o yaml > "${ns_dir}/all.yaml"
  kubectl -n "${ns}" get configmap -o yaml > "${ns_dir}/configmaps.yaml"
  kubectl -n "${ns}" get serviceaccount -o yaml > "${ns_dir}/serviceaccounts.yaml"
  kubectl -n "${ns}" get role -o yaml > "${ns_dir}/roles.yaml" || true
  kubectl -n "${ns}" get rolebinding -o yaml > "${ns_dir}/rolebindings.yaml" || true
  kubectl -n "${ns}" get ingress -o yaml > "${ns_dir}/ingress.yaml" || true
  kubectl -n "${ns}" get ingressroute -o yaml > "${ns_dir}/ingressroutes.yaml" || true
  kubectl -n "${ns}" get ingressroutetcp -o yaml > "${ns_dir}/ingressroutetcp.yaml" || true
  kubectl -n "${ns}" get middleware -o yaml > "${ns_dir}/middlewares.yaml" || true
  kubectl -n "${ns}" get pvc -o yaml > "${ns_dir}/pvcs.yaml" || true
  kubectl -n "${ns}" get networkpolicy -o yaml > "${ns_dir}/networkpolicies.yaml" || true
  kubectl -n "${ns}" get hpa -o yaml > "${ns_dir}/hpa.yaml" || true
  kubectl -n "${ns}" get pdb -o yaml > "${ns_dir}/pdb.yaml" || true
  kubectl -n "${ns}" get job -o yaml > "${ns_dir}/jobs.yaml" || true
  kubectl -n "${ns}" get cronjob -o yaml > "${ns_dir}/cronjobs.yaml" || true
  kubectl -n "${ns}" get daemonset -o yaml > "${ns_dir}/daemonsets.yaml" || true
  kubectl -n "${ns}" get statefulset -o yaml > "${ns_dir}/statefulsets.yaml" || true
  kubectl -n "${ns}" get deployment -o yaml > "${ns_dir}/deployments.yaml" || true
  kubectl -n "${ns}" get service -o yaml > "${ns_dir}/services.yaml" || true
  kubectl -n "${ns}" get endpoints -o yaml > "${ns_dir}/endpoints.yaml" || true
  kubectl -n "${ns}" get event -o yaml > "${ns_dir}/events.yaml" || true
  echo "exported ${ns}"
done
