# Kyverno

Place Kyverno policy baselines here.

Initial policy candidates:

- disallow privileged pods
- restrict hostPath
- restrict host networking
- require resource requests and limits
- disallow `latest` image tags
- require baseline labels
- restrict unsafe capabilities

Use audit mode first. Document exceptions before moving policies to enforce mode.
