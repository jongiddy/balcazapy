png(graph)
LTRE_Results <- sapply(LTRE_Analysis, sum)
names(LTRE_Results) <- xticks
# ensure 0 is included in the range, so barplot fits correctly
min.effect <- min(LTRE_Results, 0)
max.effect <- max(LTRE_Results, 0)
diff.effect <- max.effect - min.effect
extra <- diff.effect / 10
barplot(LTRE_Results, xlab=xlabel, ylab=ylabel, ylim=c(min.effect-extra, max.effect+extra),
	col=plot_colour, las=1, cex.names=0.9)
abline(h=0)
box()
title(substitute(italic(t),list(t=plot_title)))
dev.off()
LTRE_Results_RLn <- LTRE_Results
